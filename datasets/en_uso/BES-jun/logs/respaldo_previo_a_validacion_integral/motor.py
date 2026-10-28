"""Evaluador determinístico de BES-jun.

No depende de Jupyter, de una interfaz gráfica ni de un modelo de lenguaje.
No codifica rutas absolutas: localiza el expediente igual que el lector.

Firma:

    evaluar(dataset_id, pozo_id, entradas=None, fecha_referencia=None) -> dict

``entradas`` sustituye mediciones o parámetros ya leídos de la hoja. Si falta
una entrada esencial, el resultado es ``no_evaluable``: no se fuerza un sí ni un no.
Ninguna regla de este expediente está aprobada, así que
``recomendacion_operacional_autorizada`` es falso.
"""

from __future__ import annotations

import argparse
import json
import logging
import traceback
import uuid
from copy import deepcopy

from analisis.cadena import calcular_hoja
from evaluacion.contratos import (
    DATASET_ID,
    PARAMETROS_PROTEGIDOS,
    VERSION_CONTRATO,
    VERSION_MOTOR,
    VERSION_SOFTWARE,
    error_entrada,
    errores_de_salida,
    interpretar_json,
    validar_solicitud,
    validar_sustitucion,
)
from ingesta.leer_bes_jun import leer_libro
from reglas.candidatas_bes_jun import comparar_caudal_con_limites, limites_a_frecuencia
from reglas.catalogo import REGLAS, disposicion, por_id

MODELOS = (
    {"id": "M-BES-FLUIDO", "version": "transcripcion-1", "funcion": "modelo_deterministico.fluidos_bes_jun.evaluar_fluido"},
    {"id": "M-BES-BALANCE", "version": "transcripcion-1", "funcion": "modelo_deterministico.balance_bes_jun.evaluar_balance"},
    {"id": "M-BES-INTERSECCION", "version": "transcripcion-1", "funcion": "modelo_deterministico.interseccion_bes_jun.caudal_a_producir"},
)

def evaluar(dataset_id: str, pozo_id: str, entradas: dict | None = None, fecha_referencia: str | None = None,
            hojas: list[dict] | None = None, *, modo: str = "operacional", escenario_id: str | None = None) -> dict:
    try:
        respuesta = _evaluar(dataset_id, pozo_id, entradas, fecha_referencia, hojas, modo=modo, escenario_id=escenario_id)
    except Exception as exc:
        return _contener_excepcion(exc, fase="evaluar")
    return _salida_publica(respuesta)


def _evaluar(dataset_id: str, pozo_id: str, entradas: dict | None = None, fecha_referencia: str | None = None,
             hojas: list[dict] | None = None, *, modo: str = "operacional", escenario_id: str | None = None) -> dict:
    """Evalúa las reglas candidatas de una hoja de BES-jun.

    ``modo="operacional"`` solo sustituye mediciones. Los límites, la curva,
    las etapas y la geometría salen de la hoja. ``modo="simulacion"`` exige
    ``escenario_id`` y no autoriza una recomendación ni escribe la ficha.
    """
    solicitado = dataset_id if isinstance(dataset_id, str) else ""
    pozo = pozo_id if isinstance(pozo_id, str) else ""
    base = _esqueleto(solicitado, pozo, fecha_referencia, modo=modo if modo in ("operacional", "simulacion") else "operacional", escenario_id=escenario_id)
    fallos = []
    if not isinstance(modo, str) or modo not in ("operacional", "simulacion"):
        fallos.append(error_entrada("modo", "VALOR_NO_ADMITIDO", "El modo es «operacional» o «simulacion».", tipo_esperado="string"))
    if isinstance(modo, str) and modo == "simulacion" and not isinstance(escenario_id, str):
        fallos.append(error_entrada("escenario_id", "CAMPO_OBLIGATORIO" if not escenario_id else "TIPO_INVALIDO", "Un escenario hipotético necesita un identificador de texto.", tipo_esperado="string"))
    if fecha_referencia is not None and not isinstance(fecha_referencia, str):
        fallos.append(error_entrada("fecha_observacion", "TIPO_INVALIDO", "La fecha de observación es un texto o null. El valor recibido no se copia a la respuesta.", tipo_esperado="string"))
    if escenario_id is not None and not isinstance(escenario_id, str):
        fallos.append(error_entrada("escenario_id", "TIPO_INVALIDO", "El identificador de escenario es un texto o null. El valor recibido no se copia a la respuesta.", tipo_esperado="string"))
    if not isinstance(dataset_id, str) or dataset_id != DATASET_ID:
        fallos.append({"campo": "dataset_id", "codigo": "DATASET_DESCONOCIDO", "detalle": f"Este motor solo evalúa {DATASET_ID}. No se procesó el dataset solicitado."})
    if not isinstance(pozo_id, str) or not pozo_id.strip() or any(ord(c) < 32 for c in pozo_id):
        fallos.append({"campo": "pozo_id", "codigo": "IDENTIFICADOR_MAL_FORMADO", "detalle": "El identificador del pozo debe ser un texto no vacío."})
    fallos.extend(validar_sustitucion(entradas, modo if modo in ("operacional", "simulacion") else "operacional"))
    if fallos:
        return _entrada_invalida(base, fallos)
    hojas = hojas if hojas is not None else leer_libro()
    base["dataset_evaluado"] = DATASET_ID
    coincidencias = [h for h in hojas if pozo_id in (h.get("pozo"), h.get("hoja"), h.get("cluster"))]
    if not coincidencias:
        base["estado_evaluacion"] = "no_evaluable"
        base["pozo_resuelto"] = None
        base["mensajes"].append(_msg("condicion_no_evaluable", "pozo_desconocido",
                                      "No hay una hoja de este dataset con ese identificador de pozo, de cluster o de hoja."))
        return base
    if len(coincidencias) > 1:
        base["estado_evaluacion"] = "no_evaluable"
        base["identidad"] = {"estado": "ambigua", "coincidencias": [h["hoja"] for h in coincidencias]}
        base["mensajes"].append(_msg("condicion_no_evaluable", "identidad_ambigua",
                                      "Más de una hoja coincide con ese identificador. No se evalúa."))
        return base

    hoja = deepcopy(coincidencias[0])
    modificados = _aplicar_entradas(hoja, entradas or {})
    base["parametros_modificados"] = modificados
    base["pozo_resuelto"] = hoja.get("pozo")
    base["identidad"] = _identidad(hoja, pozo_id)
    if modo == "simulacion":
        base["hipotetico"] = True
        base["escenario_id"] = escenario_id
        base["advertencias"].append(
            f"Escenario hipotético {escenario_id}. No actualiza la ficha del pozo y no autoriza una recomendación operacional."
        )
    if hoja.get("fecha_es_today"):
        base["advertencias"].append("La fecha de la hoja es =TODAY(); no es una fecha histórica de medición.")
    elif hoja.get("fecha_cache"):
        base["advertencias"].append(
            "La hoja trae una fecha escrita, pero este expediente no comprobó que sea la fecha de la medición."
        )

    dominio = _dominio_observado(hojas)
    frecuencia = hoja.get("frecuencia_hz")
    if frecuencia is not None and (frecuencia < dominio["frecuencia_hz"][0] or frecuencia > dominio["frecuencia_hz"][1]):
        base["advertencias"].append(
            f"La frecuencia {frecuencia:g} Hz está fuera del dominio observado en este dataset "
            f"({dominio['frecuencia_hz'][0]:g}–{dominio['frecuencia_hz'][1]:g} Hz). "
            "El cálculo puede ejecutarse, pero el motor no lo trata como un caso validado."
        )
        base["fuera_de_dominio_observado"] = True

    try:
        cadena = calcular_hoja(hoja)
    except Exception as exc:
        return _contener_excepcion(exc, fase="modelo", dataset_evaluado=base.get("dataset_evaluado"))
    base["modelos"] = _modelos(cadena)
    if cadena["fl"].estado != "calculable" or cadena["ba"].estado != "calculable" or cadena["q"].estado != "calculable":
        base["estado_evaluacion"] = "no_evaluable"
        base["mensajes"].append(_msg(
            "condicion_no_evaluable", "modelo_no_calculable",
            "La cadena determinística no produjo un resultado calculable. No se fuerza una regla de caudal.",
        ))
        base["reglas"].append(_regla_no_evaluable("RC-BES-01", "el modelo de la hoja no es calculable"))
        base["reglas"].append(_rc04())
        return base

    observacion = comparar_caudal_con_limites(hoja, escalar=True)[0]
    artefacto = comparar_caudal_con_limites(hoja, escalar=False)[0]
    if observacion["resultado"] == "no_evaluable":
        base["estado_evaluacion"] = "no_evaluable"
        base["mensajes"].append(_msg("condicion_no_evaluable", "dato_insuficiente", observacion.get("motivo", "Faltan datos.")))
        base["reglas"].append(_regla_no_evaluable("RC-BES-01", observacion.get("motivo", "dato insuficiente")))
        base["reglas"].append(_rc04())
        return base

    ficha = por_id(observacion["id"])
    if disposicion(ficha) == "no_ejecutar":
        base["estado_evaluacion"] = "no_evaluable"
        base["reglas"].append(_regla_no_evaluable(ficha["id"], f"La regla está {ficha['estado_validacion']} y no se ejecuta."))
        base["reglas"].append(_rc04())
        return base
    base["reglas"].append(_regla_activada(ficha, observacion, artefacto, hoja))
    for identificador in ("RC-BES-01", "RC-BES-02", "RC-BES-03"):
        if identificador != observacion["id"]:
            base["reglas"].append(_regla_no_activada(por_id(identificador)))
    base["reglas"].append(_rc04())
    base["estado_evaluacion"] = "completada_preliminar"
    base["reglas_ejecutadas"] = 3
    base["recomendacion_operacional_autorizada"] = False
    return base


def evaluar_solicitud(solicitud: dict, hojas: list[dict] | None = None) -> dict:
    """Valida el contrato de entrada y solo entonces evalúa."""
    try:
        return _salida_publica(_evaluar_solicitud(solicitud, hojas))
    except Exception as exc:
        return _contener_excepcion(exc, fase="solicitud")


def _evaluar_solicitud(solicitud: dict, hojas: list[dict] | None = None) -> dict:
    if not isinstance(solicitud, dict):
        return _entrada_invalida(_esqueleto("", "", None), validar_solicitud(solicitud))
    fallos = validar_solicitud(solicitud)
    modo = solicitud.get("modo") or "operacional"
    fecha = solicitud.get("fecha_observacion")
    dataset = solicitud.get("dataset_id", "")
    pozo = solicitud.get("pozo_id", "")
    if fallos:
        return _entrada_invalida(
            _esqueleto(dataset if isinstance(dataset, str) else "", pozo if isinstance(pozo, str) else "", fecha, modo if modo in ("operacional", "simulacion") else "operacional", solicitud.get("escenario_id")),
            fallos,
        )
    variables = {}
    unidades = {}
    for item in solicitud.get("variables") or []:
        variables[item["nombre"]] = item["valor"]
        unidades[item["nombre"]] = item["unidad"]
    for clave, especificado in (solicitud.get("parametros_escenario") or {}).items():
        if clave in ("bomba_referencia", "curva"):
            variables[clave] = especificado
        else:
            variables[clave] = especificado["valor"]
            unidades[clave] = especificado["unidad"]
    if unidades:
        variables["unidades"] = unidades
    return _evaluar(
        solicitud["dataset_id"], solicitud["pozo_id"], variables or None, fecha, hojas=hojas,
        modo=modo if isinstance(modo, str) else "operacional", escenario_id=solicitud.get("escenario_id"),
    )


def evaluar_json(texto: str, hojas: list[dict] | None = None) -> dict:
    """Interfaz de texto JSON. Las claves repetidas no se descartan."""
    try:
        documento, fallos = interpretar_json(texto)
        if fallos:
            return _salida_publica(_entrada_invalida(_esqueleto("", "", None), fallos))
        return evaluar_solicitud(documento, hojas=hojas)
    except Exception as exc:
        return _contener_excepcion(exc, fase="json")


def _esqueleto(dataset_id, pozo_id, fecha_referencia, modo="operacional", escenario_id=None) -> dict:
    from reglas.catalogo import VERSION_CATALOGO
    return {
        "dataset_solicitado": _texto(dataset_id),
        "dataset_evaluado": None,
        "pozo_solicitado": _texto(pozo_id),
        "pozo_resuelto": None,
        "version_contrato": VERSION_CONTRATO,
        "version_motor": VERSION_MOTOR,
        "version_catalogo_reglas": VERSION_CATALOGO,
        "version_software": VERSION_SOFTWARE,
        "fecha_referencia": _opcional(fecha_referencia),
        "incidente_id": None,
        "estado_evaluacion": "entrada_invalida",
        "identidad": {"estado": "no_resuelta"},
        "modelos": [],
        "reglas": [],
        "advertencias": [],
        "mensajes": [],
        "errores": [],
        "reglas_ejecutadas": 0,
        "recomendacion_operacional_autorizada": False,
        "fuera_de_dominio_observado": False,
        "modo": modo if modo in ("operacional", "simulacion") else "operacional",
        "hipotetico": modo == "simulacion",
        "escenario_id": _opcional(escenario_id),
        "parametros_modificados": [],
    }


def _entrada_invalida(base: dict, errores: list[dict]) -> dict:
    """Solicitud rechazada. No llama a los modelos."""
    base["estado_evaluacion"] = "entrada_invalida"
    base["dataset_evaluado"] = None
    base["pozo_resuelto"] = None
    base["modelos"] = []
    base["reglas"] = []
    base["errores"] = errores
    base["reglas_ejecutadas"] = 0
    base["recomendacion_operacional_autorizada"] = False
    for fallo in errores:
        base["mensajes"].append(_msg("error_dato", fallo["codigo"], f"{fallo['campo']}: {fallo['detalle']}"))
    return base


def _msg(tipo: str, codigo: str, texto: str) -> dict:
    return {"tipo": tipo, "codigo": codigo, "texto": texto}


def _aplicar_entradas(hoja: dict, entradas: dict) -> list[str]:
    """Copia sustituciones ya validadas. No escribe el libro ni la ficha de origen."""
    modificados = []
    for clave, valor in entradas.items():
        if clave != "unidades":
            hoja[clave] = valor
            if clave in PARAMETROS_PROTEGIDOS:
                modificados.append(clave)
    return modificados


def _texto(valor, maximo: int = 200) -> str:
    if isinstance(valor, str) and len(valor) <= maximo and all(ord(caracter) >= 32 for caracter in valor):
        return valor
    return ""


def _opcional(valor, maximo: int = 200):
    texto = _texto(valor, maximo)
    return texto or None


def _salida_publica(respuesta: dict) -> dict:
    """Ninguna respuesta sale si no cumple el esquema publicado."""
    if errores_de_salida(respuesta):
        return _contener_excepcion(RuntimeError("respuesta_fuera_de_esquema"), fase="salida")
    return respuesta


def _contener_excepcion(exc: Exception, fase: str, dataset_evaluado: str | None = None) -> dict:
    """Barrera de la entrada pública. La traza queda en el registro, no en la respuesta."""
    incidente = "INC-" + uuid.uuid4().hex[:12]
    _registrar_incidente(incidente, exc, fase)
    base = _esqueleto("", "", None)
    base["estado_evaluacion"] = "error_interno"
    base["incidente_id"] = incidente
    if dataset_evaluado == DATASET_ID:
        base["dataset_evaluado"] = DATASET_ID
    base["errores"] = [error_entrada(
        "evaluacion", "ERROR_INTERNO",
        "No fue posible completar la evaluación. Revise los datos o contacte al responsable técnico.",
    )]
    base["mensajes"] = [_msg("error_dato", "ERROR_INTERNO", "La evaluación no se completó. No hay recomendación operacional.")]
    base["modelos"] = []
    base["reglas"] = []
    base["reglas_ejecutadas"] = 0
    base["recomendacion_operacional_autorizada"] = False
    return base


def _registrar_incidente(incidente: str, exc: Exception, fase: str) -> None:
    try:
        from ingesta.leer_bes_jun import raiz_expediente
        ruta = raiz_expediente() / "logs" / "incidentes.jsonl"
        ruta.parent.mkdir(parents=True, exist_ok=True)
        linea = json.dumps({
            "incidente_id": incidente,
            "fase": fase,
            "tipo": type(exc).__name__,
            "traza": traceback.format_exc()[-2000:],
        }, ensure_ascii=False)
        with ruta.open("a", encoding="utf-8") as archivo:
            archivo.write(linea + "\n")
    except Exception:
        logging.getLogger("evaluacion.incidentes").debug("incidente %s no registrado", incidente)


def _identidad(hoja: dict, solicitado: str) -> dict:
    return {
        "estado": "provisional",
        "pozo_id_solicitado": solicitado,
        "hoja": hoja.get("hoja"),
        "cluster": hoja.get("cluster"),
        "pozo_rotulo": hoja.get("pozo"),
        "coincide_con": "pozo" if solicitado == hoja.get("pozo") else "hoja_o_cluster",
        "motivo": "Dentro de este archivo la hoja es única, pero el libro no declara si la llave global es Cluster o Pozo.",
    }


def _dominio_observado(hojas: list[dict]) -> dict:
    frecuencias = [h["frecuencia_hz"] for h in hojas if h.get("frecuencia_hz") is not None]
    return {"frecuencia_hz": (min(frecuencias), max(frecuencias))}


def _modelos(cadena: dict) -> list[dict]:
    salida = []
    for modelo, etapa, claves in (
        (MODELOS[0], cadena["fl"], ("gradiente_psi_ft",)),
        (MODELOS[1], cadena["ba"], ("pip_ft", "thd_total_ft")),
        (MODELOS[2], cadena["q"], ("caudal_a_producir_bfpd",)),
    ):
        valores = {}
        for clave in claves:
            celda = etapa.resultados.get(clave) or {}
            valores[clave] = celda.get("valor")
        salida.append({**modelo, "estado": etapa.estado, "valores": valores, "alertas": list(etapa.alertas)})
    return salida


def _regla_activada(ficha: dict, observacion: dict, artefacto: dict, hoja: dict) -> dict:
    limites = limites_a_frecuencia(hoja, escalar=True)
    tipo = "advertencia" if observacion["id"] in ("RC-BES-01", "RC-BES-02") else "observacion"
    return {
        "id": observacion["id"],
        "version": ficha["version"],
        "estado_regla": ficha["estado_validacion"],
        "resultado": observacion["resultado"],
        "evaluable": True,
        "activada": True,
        "aprobada_para_uso_operacional": False,
        "tipo_mensaje": tipo,
        "mensaje": ficha["mensaje_si_se_cumple"],
        "evidencia": {
            "caudal_operacion_bfpd": observacion.get("caudal_bfpd"),
            "frecuencia_operacion_hz": observacion.get("frecuencia_operacion_hz"),
            "limite_minimo_a_frecuencia_bfpd": None if limites is None else limites["minimo_bfpd"],
            "limite_maximo_a_frecuencia_bfpd": None if limites is None else limites["maximo_bfpd"],
            "limite_maximo_escrito_a_60_hz_bfpd": hoja.get("limite_maximo_bfpd"),
            "uso_del_limite_maximo_pct": observacion.get("uso_del_limite_maximo_pct"),
            "comparacion_sin_escalar": {
                "id": artefacto.get("id"),
                "resultado": artefacto.get("resultado"),
                "nota": "Mezcla la frecuencia de operación con el límite a 60 Hz. No es la clasificación vigente.",
            },
        },
        "limitaciones": list(ficha["limitaciones"]),
        "consultas_tecnicas": list(ficha["consultas_tecnicas"]),
    }


def _regla_no_activada(ficha: dict) -> dict:
    return {
        "id": ficha["id"],
        "version": ficha["version"],
        "estado_regla": ficha["estado_validacion"],
        "resultado": "no_activada",
        "evaluable": True,
        "activada": False,
        "aprobada_para_uso_operacional": False,
        "tipo_mensaje": "informacion",
        "mensaje": "Esta condición no se cumple en el punto evaluado. Sigue pendiente de validación.",
        "evidencia": {},
        "limitaciones": list(ficha["limitaciones"]),
        "consultas_tecnicas": list(ficha["consultas_tecnicas"]),
    }


def _regla_no_evaluable(identificador: str, motivo: str) -> dict:
    ficha = por_id(identificador) if identificador in {r["id"] for r in REGLAS} else {"version": "1.1.0", "limitaciones": [], "consultas_tecnicas": []}
    return {
        "id": identificador,
        "version": ficha.get("version", "1.1.0"),
        "estado_regla": "pendiente_validacion",
        "resultado": "no_evaluable",
        "evaluable": False,
        "activada": False,
        "aprobada_para_uso_operacional": False,
        "tipo_mensaje": "condicion_no_evaluable",
        "mensaje": motivo,
        "evidencia": {},
        "limitaciones": list(ficha.get("limitaciones") or []),
        "consultas_tecnicas": list(ficha.get("consultas_tecnicas") or []),
    }


def _rc04() -> dict:
    ficha = por_id("RC-BES-04")
    return {
        "id": "RC-BES-04",
        "version": ficha["version"],
        "estado_regla": "no_evaluable",
        "resultado": "no_evaluable",
        "evaluable": False,
        "activada": False,
        "aprobada_para_uso_operacional": False,
        "tipo_mensaje": "condicion_no_evaluable",
        "mensaje": ficha["mensaje_si_se_cumple"],
        "evidencia": {},
        "limitaciones": list(ficha["limitaciones"]),
        "consultas_tecnicas": list(ficha["consultas_tecnicas"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evalúa las reglas candidatas de un pozo de BES-jun.")
    parser.add_argument("--dataset", default=DATASET_ID)
    parser.add_argument("--pozo", required=True)
    parser.add_argument("--caudal", type=float, default=None, help="Sustituye el caudal de operación, en BFPD.")
    parser.add_argument("--frecuencia", type=float, default=None, help="Sustituye la frecuencia, en Hz.")
    args = parser.parse_args()
    entradas = {}
    unidades = {}
    if args.caudal is not None:
        entradas["caudal_operacion_bfpd"] = args.caudal
        unidades["caudal_operacion_bfpd"] = "BFPD"
    if args.frecuencia is not None:
        entradas["frecuencia_hz"] = args.frecuencia
        unidades["frecuencia_hz"] = "Hz"
    if unidades:
        entradas["unidades"] = unidades
    print(json.dumps(evaluar(args.dataset, args.pozo, entradas or None), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
