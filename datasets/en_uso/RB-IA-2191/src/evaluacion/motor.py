"""Evaluación de RB-IA-2191. Calcula BOPD = BFPD − BWPD; no estima bomba ni presión."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from rbia2191_lectura import HASH_ORIGINAL, dia_referencia, fecha_iso, huella, leer_serie
from rbia2191_particion import contar_identidades, identidad_exacta, particionar

DATASET_ID = "RB-IA-2191"
POZO_ID = "RB-IA-2191"


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
    bfpd, bwpd = caudales
    bopd = particionar(bfpd, bwpd)
    coincide = (
        abs(bfpd - float(referencia["BFPD"])) <= 1e-9
        and abs(bwpd - float(referencia["BWPD"])) <= 1e-9
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
            "id": "M-RBIA2191-BOPD",
            "valores": {
                "bfpd": bfpd,
                "bwpd": bwpd,
                "bopd": bopd,
                "bsw": float(referencia["BSW"]),
                "frecuencia_hz": float(referencia["HZ"]),
                "pip": float(referencia["PIP"]) if referencia.get("PIP") is not None else None,
                "dias_serie": float(len(serie)),
                "dias_identidad_exacta": float(contar_identidades(serie)),
            },
            "etiquetas": {
                "bfpd": {"nombre": "BFPD", "unidad": "BFPD"},
                "bwpd": {"nombre": "BWPD", "unidad": "BFPD"},
                "bopd": {"nombre": "BOPD", "unidad": "BFPD"},
                "bsw": {"nombre": "BSW (almacenado)", "unidad": "fracción", "decimales": 3},
                "frecuencia_hz": {"nombre": "HZ", "unidad": "Hz"},
                "pip": {"nombre": "PIP (almacenado)", "unidad": ""},
                "dias_serie": {"nombre": "Días de la serie", "unidad": "d"},
                "dias_identidad_exacta": {"nombre": "Días en que BOPD = BFPD − BWPD", "unidad": "d"},
            },
        }],
        "parametros_modificados": [],
        "coincidencia_dia_referencia": coincide,
        "fecha_referencia": fecha_iso(referencia["FECHA"]),
    }


def _leer_entradas(solicitud: dict, referencia: dict) -> tuple[tuple[float, float] | None, str]:
    bfpd = float(referencia["BFPD"])
    bwpd = float(referencia["BWPD"])
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
        if nombre == "bfpd":
            if item.get("unidad") not in (None, "BFPD"):
                return None, "La unidad de bfpd debe ser BFPD."
            bfpd = float(valor)
        elif nombre == "bwpd":
            if item.get("unidad") not in (None, "BFPD"):
                return None, "La unidad de bwpd debe ser BFPD."
            bwpd = float(valor)
        else:
            return None, f"{nombre} no entra en el cálculo BOPD de este expediente."
    if bfpd < 0 or bwpd < 0:
        return None, "Los caudales no pueden ser negativos."
    if bwpd > bfpd:
        return None, "BWPD no puede superar a BFPD en esta identidad."
    return (bfpd, bwpd), ""


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
