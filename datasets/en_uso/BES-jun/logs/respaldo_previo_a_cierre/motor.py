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
from copy import deepcopy

from analisis.cadena import calcular_hoja
from evaluacion.contratos import DATASET_ID, UNIDADES_CANONICAS, VERSION_CONTRATO, validar_solicitud, validar_sustitucion
from ingesta.leer_bes_jun import leer_libro
from reglas.candidatas_bes_jun import comparar_caudal_con_limites, limites_a_frecuencia
from reglas.catalogo import REGLAS, disposicion, por_id

VERSION_MOTOR = "0.2.0"
MODELOS = (
    {"id": "M-BES-FLUIDO", "version": "transcripcion-1", "funcion": "modelo_deterministico.fluidos_bes_jun.evaluar_fluido"},
    {"id": "M-BES-BALANCE", "version": "transcripcion-1", "funcion": "modelo_deterministico.balance_bes_jun.evaluar_balance"},
    {"id": "M-BES-INTERSECCION", "version": "transcripcion-1", "funcion": "modelo_deterministico.interseccion_bes_jun.caudal_a_producir"},
)

CLAVES_SUSTITUIBLES = frozenset(UNIDADES_CANONICAS)


def evaluar(dataset_id: str, pozo_id: str, entradas: dict | None = None, fecha_referencia: str | None = None,
            hojas: list[dict] | None = None) -> dict:
    """Evalúa las reglas candidatas de una hoja de BES-jun."""
    base = _esqueleto(dataset_id if isinstance(dataset_id, str) else "", pozo_id if isinstance(pozo_id, str) else "", fecha_referencia)
    fallos = []
    if not isinstance(dataset_id, str) or dataset_id != DATASET_ID:
        fallos.append({"campo": "dataset_id", "codigo": "DATASET_DESCONOCIDO", "detalle": f"Este motor solo evalúa {DATASET_ID}."})
    if not isinstance(pozo_id, str) or not pozo_id.strip() or any(ord(c) < 32 for c in pozo_id):
        fallos.append({"campo": "pozo_id", "codigo": "IDENTIFICADOR_MAL_FORMADO", "detalle": "El identificador del pozo debe ser un texto no vacío."})
    fallos.extend(validar_sustitucion(entradas))
    if fallos:
        return _entrada_invalida(base, fallos)
    hojas = hojas if hojas is not None else leer_libro()
    coincidencias = [h for h in hojas if pozo_id in (h.get("pozo"), h.get("hoja"), h.get("cluster"))]
    if not coincidencias:
        base["estado_evaluacion"] = "no_evaluable"
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
    _aplicar_entradas(hoja, entradas or {})
    base["identidad"] = _identidad(hoja, pozo_id)
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

    cadena = calcular_hoja(hoja)
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
    fallos = validar_solicitud(solicitud)
    if fallos:
        dataset = solicitud.get("dataset_id", "") if isinstance(solicitud, dict) else ""
        pozo = solicitud.get("pozo_id", "") if isinstance(solicitud, dict) else ""
        fecha = solicitud.get("fecha_observacion") if isinstance(solicitud, dict) else None
        return _entrada_invalida(_esqueleto(dataset if isinstance(dataset, str) else "", pozo if isinstance(pozo, str) else "", fecha), fallos)
    variables = {}
    unidades = {}
    for item in solicitud.get("variables") or []:
        variables[item["nombre"]] = item["valor"]
        unidades[item["nombre"]] = item["unidad"]
    if unidades:
        variables["unidades"] = unidades
    return evaluar(solicitud["dataset_id"], solicitud["pozo_id"], variables or None, solicitud.get("fecha_observacion"), hojas=hojas)


def _esqueleto(dataset_id, pozo_id, fecha_referencia) -> dict:
    return {
        "dataset_id": dataset_id,
        "pozo_id": pozo_id,
        "version_contrato": VERSION_CONTRATO,
        "version_motor": VERSION_MOTOR,
        "version_catalogo_reglas": "1.1.0",
        "fecha_referencia": fecha_referencia,
        "estado_evaluacion": "error_validacion",
        "identidad": {"estado": "no_resuelta"},
        "modelos": [],
        "reglas": [],
        "advertencias": [],
        "mensajes": [],
        "errores": [],
        "reglas_ejecutadas": 0,
        "recomendacion_operacional_autorizada": False,
        "fuera_de_dominio_observado": False,
    }


def _entrada_invalida(base: dict, errores: list[dict]) -> dict:
    """Solicitud rechazada. No llama a los modelos."""
    base["estado_evaluacion"] = "entrada_invalida"
    base["errores"] = errores
    base["reglas_ejecutadas"] = 0
    base["recomendacion_operacional_autorizada"] = False
    for fallo in errores:
        base["mensajes"].append(_msg("error_dato", fallo["codigo"], f"{fallo['campo']}: {fallo['detalle']}"))
    return base


def _msg(tipo: str, codigo: str, texto: str) -> dict:
    return {"tipo": tipo, "codigo": codigo, "texto": texto}


def _aplicar_entradas(hoja: dict, entradas: dict) -> None:
    """Copia sustituciones ya validadas. No interpreta unidades ni tipos."""
    for clave, valor in entradas.items():
        if clave != "unidades":
            hoja[clave] = valor


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
