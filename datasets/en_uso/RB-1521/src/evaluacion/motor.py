"""Evaluación de RB-1521. Reparte el caudal; no estima presión ni head de bomba."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from rb1521_lectura import HASH_ORIGINAL, dia_referencia, fecha_iso, huella, leer_serie
from rb1521_particion import contar_identidades, identidad_exacta, particionar

DATASET_ID = "RB-1521"
POZO_ID = "RB-1521"


def evaluar_solicitud(solicitud: dict) -> dict:
    if not isinstance(solicitud, dict):
        return _error("entrada_invalida", "La solicitud no es un objeto.")
    if solicitud.get("dataset_id") not in (None, DATASET_ID):
        return _error("entrada_invalida", "La solicitud corresponde a otro dataset.")
    if solicitud.get("pozo_id") not in (None, POZO_ID):
        return _error("entrada_invalida", "Ese identificador no está en este libro.")
    if huella() != HASH_ORIGINAL:
        return _error("error_interno", "La copia de trabajo no conserva el hash del original.")
    try:
        serie = leer_serie()
    except (OSError, ValueError) as exc:
        return _error("error_interno", exc.__class__.__name__)
    referencia = dia_referencia(serie)
    caudales, error = _leer_entradas(solicitud, referencia)
    if error:
        return _error("entrada_invalida", error)
    caudal, bsw = caudales
    agua, petroleo = particionar(caudal, bsw)
    coincide = (
        abs(caudal - float(referencia["Q-fluidos"])) <= 1e-9
        and abs(bsw - float(referencia["BSW"])) <= 1e-12
        and identidad_exacta(referencia)
    )
    return {
        "estado_evaluacion": "completada_preliminar",
        "dataset_evaluado": DATASET_ID,
        "pozo_solicitado": POZO_ID,
        "recomendacion_operacional_autorizada": False,
        "resultados_sin_regla": True,
        "errores": [],
        "advertencias": [],
        "mensajes": [],
        "reglas": [],
        "modelos": [{
            "id": "M-RB1521-PARTICION",
            "valores": {
                "q_fluidos": caudal,
                "bsw": bsw,
                "q_water": agua,
                "q_oil": petroleo,
                "dias_serie": float(len(serie)),
                "dias_identidad_exacta": float(contar_identidades(serie)),
            },
            "etiquetas": {
                "q_fluidos": {"nombre": "Q-fluidos", "unidad": "BFPD"},
                "bsw": {"nombre": "BSW", "unidad": "fracción", "decimales": 3},
                "q_water": {"nombre": "Q-water", "unidad": "BFPD"},
                "q_oil": {"nombre": "Q-oil", "unidad": "BFPD"},
                "dias_serie": {"nombre": "Días de la serie", "unidad": "d"},
                "dias_identidad_exacta": {"nombre": "Días en que la partición cierra", "unidad": "d"},
            },
        }],
        "parametros_modificados": [],
        "coincidencia_dia_referencia": coincide,
        "fecha_referencia": fecha_iso(referencia["Fecha"]),
    }


def _leer_entradas(solicitud: dict, referencia: dict) -> tuple[tuple[float, float] | None, str]:
    caudal = float(referencia["Q-fluidos"])
    bsw = float(referencia["BSW"])
    variables = solicitud.get("variables") or []
    if not isinstance(variables, list):
        return None, "Las variables no son una lista."
    for item in variables:
        if not isinstance(item, dict):
            return None, "Una variable no es un objeto."
        nombre = item.get("nombre")
        valor = item.get("valor")
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            return None, f"{nombre} no es un número."
        if nombre == "caudal_fluidos":
            if item.get("unidad") not in (None, "BFPD"):
                return None, "La unidad de caudal_fluidos debe ser BFPD."
            caudal = float(valor)
        elif nombre == "bsw":
            if item.get("unidad") not in (None, "fracción"):
                return None, "La unidad de bsw debe ser fracción."
            bsw = float(valor)
        else:
            return None, f"{nombre} no entra en la partición de este expediente."
    if caudal < 0 or not 0 <= bsw <= 1:
        return None, "El caudal no puede ser negativo y el BSW tiene que estar entre 0 y 1."
    return (caudal, bsw), ""


def _error(estado: str, mensaje: str) -> dict:
    return {
        "estado_evaluacion": estado,
        "dataset_evaluado": DATASET_ID if estado != "entrada_invalida" else None,
        "pozo_solicitado": POZO_ID,
        "recomendacion_operacional_autorizada": False,
        "errores": [{"codigo": estado.upper(), "mensaje": mensaje}],
        "advertencias": [],
        "mensajes": [],
        "reglas": [],
        "modelos": [],
    }
