"""Orquesta la consola: ficha, motor, estado y texto. No escribe el dataset."""

from __future__ import annotations

import math
from datetime import datetime, timezone

from services.rule_control_registry import definicion_entrada, dominios_de
from services.formato_numero import formato_visible
from services.escenario_inicial import escenario_de, listar_pozos, localizar
from services.estado_operacional import clasificar
from services.huc_adapter import adaptador_para
from services.mensajes_operador import explicar, mensaje_deterministico

_ESTADOS_INICIALES: dict[tuple, dict] = {}

FUENTE_INICIAL = (
    "Evaluación determinística del escenario inicial de la ficha. "
    "No es telemetría ni un resultado histórico."
)
NOTA_LISTA = ""


def estados_iniciales() -> dict:
    """Clasifica el escenario de ficha de cada pozo. No llama al asistente."""
    pozos = listar_pozos()
    firma = tuple((item["pozo_id"], item["dataset_id"]) for item in pozos)
    guardado = _ESTADOS_INICIALES.get(firma)
    if guardado is not None:
        return guardado
    filas = [_fila_de_evaluacion(item["pozo_id"]) for item in pozos]
    cuerpo = {"fuente": "escenario_inicial", "nota": NOTA_LISTA, "pozos": filas}
    _ESTADOS_INICIALES[firma] = cuerpo
    return cuerpo


def _fila_de_evaluacion(pozo_id: str) -> dict:
    codigo, cuerpo = evaluar_pozo(pozo_id, {}, "", f"inicial-{pozo_id}", False)
    estado = cuerpo.get("estado") if codigo == 200 and isinstance(cuerpo, dict) else {}
    if not isinstance(estado, dict):
        estado = {}
    valida = estado.get("clasificacion_valida") is True
    tono = estado.get("tono") if valida else "sin-clasificacion"
    if tono not in ("normal", "incipiente", "critico"):
        tono = "sin-clasificacion"
        valida = False
    return {
        "pozo_id": pozo_id,
        "codigo": estado.get("codigo") or "SIN_DATOS",
        "rotulo": estado.get("rotulo") or "SIN CLASIFICACIÓN OPERACIONAL",
        "tono": tono,
        "clasificacion_valida": valida,
        "origen": "escenario_inicial",
        "fuente": "Medición registrada en la hoja, comparada con las reglas de caudal.",
        "mensaje": (cuerpo.get("texto") or {}).get("mensaje") or "",
    }


ENTRADAS = {
    "frecuencia_hz": "Hz",
    "caudal_operacion_bfpd": "BFPD",
}


def evaluar_pozo(pozo_id: str, controles: dict, escenario_id: str, evaluacion_id: str, explicar_con_modelo: bool) -> tuple[int, dict]:
    encontrados = localizar(pozo_id)
    if not encontrados:
        return 404, {"ok": False, "error": "Ese pozo no está en una ficha de integración."}
    if len(encontrados) > 1:
        return 409, {"ok": False, "error": "Hay más de un pozo con ese identificador. No se evalúa."}
    ficha, pozo = encontrados[0]
    escenario = escenario_de(pozo, ficha)
    if not ficha.puede_evaluar:
        cuerpo = _respuesta(escenario, evaluacion_id, escenario_id, [], {
            "estado_evaluacion": "no_disponible",
            "recomendacion_operacional_autorizada": False,
            "errores": [{"mensaje": ficha.causa_sin_evaluacion}],
            "reglas": [],
            "modelos": [],
            "advertencias": [],
        }, simular=False)
        return 200, cuerpo

    try:
        cambios, errores = _cambios(ficha, escenario, controles)
    except TypeError:
        return 400, {"ok": False, "error": "Los controles deben ser un objeto de números."}
    if errores:
        return 400, {"ok": False, "error": " ".join(errores), "evaluacion_id": evaluacion_id}

    variables = []
    parametros = {}
    for nombre, valor in cambios.items():
        via = definicion_entrada(ficha, nombre)["via"]
        unidad = definicion_entrada(ficha, nombre).get("unidad") or ENTRADAS.get(nombre, "")
        if via == "variable":
            variables.append({
                "nombre": nombre,
                "valor": valor,
                "unidad": unidad,
                "procedencia": "operador",
            })
        elif via == "parametro_escenario":
            parametros[nombre] = {"valor": valor, "unidad": unidad}
    simular = bool(cambios)
    identificador = escenario_id or f"sim-{pozo_id}"
    salida = adaptador_para(ficha).evaluar_escenario(pozo_id, variables, parametros, identificador, simular)
    cuerpo = _respuesta(escenario, evaluacion_id, identificador, sorted(cambios), salida, simular)
    frecuencia = next((control["valor_inicial"] for control in escenario["controles"] if control["id"] == "frecuencia_hz"), None)
    if "frecuencia_hz" in cambios:
        frecuencia = cambios["frecuencia_hz"]
    cuerpo["dominios"] = dominios_de(pozo, ficha, frecuencia)
    if explicar_con_modelo and cuerpo["ok"]:
        texto = explicar(cuerpo["estado"], cuerpo["texto"], sorted(cambios), cuerpo["resultados"])
        cuerpo["texto"] = texto
        cuerpo["estado_fijado_por"] = "motor"
    return 200, cuerpo


def _cambios(ficha, escenario: dict, controles: dict) -> tuple[dict, list[str]]:
    if controles is None:
        controles = {}
    if not isinstance(controles, dict):
        raise TypeError("controles")
    iniciales = {control["id"]: control["valor_inicial"] for control in escenario["controles"]}
    errores = []
    cambios = {}
    for nombre, crudo in controles.items():
        definicion_control = definicion_entrada(ficha, str(nombre))
        if definicion_control is None or definicion_control["rol"] != "entrada":
            errores.append(f"{nombre} no es un mando de entrada.")
            continue
        if isinstance(crudo, dict):
            unidad_esperada = definicion_control.get("unidad") or ENTRADAS.get(nombre, "")
            if "unidad" in crudo and crudo["unidad"] != unidad_esperada:
                errores.append(f"La unidad de {nombre} debe ser {unidad_esperada}.")
                continue
            crudo = crudo.get("valor")
        if isinstance(crudo, bool) or not isinstance(crudo, (int, float)) or not math.isfinite(float(crudo)):
            errores.append(f"{nombre} no es un número finito. No se sustituye por cero.")
            continue
        valor = float(crudo)
        if nombre == "frecuencia_hz" and valor <= 0:
            errores.append("La frecuencia tiene que ser mayor que cero. El expediente no define otro límite operacional.")
            continue
        inicial = iniciales.get(nombre)
        if inicial is not None and abs(valor - inicial) <= 1e-6 * max(1.0, abs(inicial)):
            continue
        cambios[nombre] = valor
    return cambios, errores


def _respuesta(escenario, evaluacion_id, escenario_id, modificadas, salida, simular: bool) -> dict:
    clasificacion = clasificar(salida)
    texto = mensaje_deterministico(clasificacion, salida, modificadas)
    resultados = _resultados(salida)
    return {
        "ok": clasificacion["codigo"] != "ERROR_CALCULO",
        "evaluacion_id": evaluacion_id,
        "escenario_id": escenario_id if simular else None,
        "pozo_id": escenario["pozo_id"],
        "hoja": escenario["hoja"],
        "dataset_id": escenario["dataset_id"],
        "modo": "simulacion" if simular else "escenario_inicial",
        "leyenda": "" if not simular else "Simulación. Los valores modificados no se escribieron en el dataset.",
        "modificadas": modificadas,
        "estado": clasificacion,
        "texto": texto,
        "resultados": resultados,
        "advertencias_motor": salida.get("advertencias") or [],
        "recomendacion_operacional_autorizada": salida.get("recomendacion_operacional_autorizada"),
        "estado_motor": salida.get("estado_evaluacion"),
        "momento_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "estado_fijado_por": "motor",
        "reglas_activas": [
            regla.get("id") for regla in salida.get("reglas") or []
            if isinstance(regla, dict) and regla.get("activada")
        ],
        "aplicadas": salida.get("parametros_modificados") or [],
    }


def _magnitud(valor, unidad: str, origen: str, nota: str, nombre: str = "", decimales: int | None = None) -> dict:
    if decimales is None:
        visible = formato_visible(valor)
    elif valor is None:
        visible = None
    else:
        visible = f"{float(valor):.{decimales}f}".rstrip("0").rstrip(".")
    return {
        "valor": valor,
        "valor_visible": visible,
        "unidad": unidad,
        "origen": origen,
        "nota": nota,
        "nombre": nombre,
    }


def _resultados(salida: dict) -> dict:
    valores = {}
    etiquetas = {}
    for modelo in salida.get("modelos") or []:
        if isinstance(modelo, dict):
            for clave, valor in (modelo.get("valores") or {}).items():
                valores[clave] = valor
            for clave, meta in (modelo.get("etiquetas") or {}).items():
                if isinstance(meta, dict):
                    etiquetas[clave] = meta
    if "pip_ft" in valores or "thd_total_ft" in valores or "caudal_a_producir_bfpd" in valores:
        return {
            "pip_ft": _magnitud(valores.get("pip_ft"), "ft", "calculado",
                                "Valor transcrito de la celda de la hoja.", "PIP"),
            "thd_total_ft": _magnitud(valores.get("thd_total_ft"), "ft", "calculado",
                                      "Salida del balance. No es un head de consigna.", "THD"),
            "caudal_a_producir_bfpd": _magnitud(valores.get("caudal_a_producir_bfpd"), "BFPD", "calculado",
                                                "Intersección de la curva con el THD. No es el caudal registrado.", "Caudal calculado"),
            "gradiente_psi_ft": _magnitud(valores.get("gradiente_psi_ft"), "psi/ft", "calculado",
                                          "La hoja lo rotula psi*ft. La cuenta es psi/ft.", "Gradiente"),
        }
    salida_valores = {}
    for clave, valor in valores.items():
        meta = etiquetas.get(clave) or {}
        salida_valores[clave] = _magnitud(
            valor,
            meta.get("unidad") or "",
            "calculado",
            "",
            meta.get("nombre") or clave,
            meta.get("decimales"),
        )
    return salida_valores
