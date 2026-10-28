"""Contratos MQTT v1. No calculan y no conservan historial."""

from __future__ import annotations

import os
import re
from datetime import datetime

VERSION = "1"
HOST = os.environ.get("HUC_MQTT_HOST", "127.0.0.1")
PUERTO = int(os.environ.get("HUC_MQTT_PORT", "1883"))
POZO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,40}$")
ENTRADAS = {
    "frecuencia_hz": "Hz",
    "caudal_operacion_bfpd": "BFPD",
}


def topic_escenario(pozo_id: str) -> str:
    _exigir_pozo(pozo_id)
    return f"huc/v1/data/{pozo_id}/escenario"


def topic_resultado(pozo_id: str) -> str:
    _exigir_pozo(pozo_id)
    return f"huc/v1/proceso/{pozo_id}/resultado"


def topic_estado(pozo_id: str) -> str:
    _exigir_pozo(pozo_id)
    return f"huc/v1/proceso/{pozo_id}/estado"


TOPIC_SERVICIO = "huc/v1/servicios/proceso/estado"


def _exigir_pozo(pozo_id: str) -> None:
    if not isinstance(pozo_id, str) or not POZO.match(pozo_id):
        raise ValueError("identificador de pozo no admisible en un topic")


def validar_escenario(documento: dict) -> str | None:
    if not isinstance(documento, dict):
        return "el mensaje no es un objeto"
    if documento.get("version") != VERSION:
        return "versión de mensaje no admitida"
    if documento.get("origen") != "data":
        return "el escenario no viene de DATA"
    pozo = documento.get("pozo_id")
    try:
        _exigir_pozo(pozo)
    except ValueError as exc:
        return str(exc)
    entradas, fallo = _entradas(documento.get("dataset_id"), pozo)
    if fallo:
        return fallo
    if entradas is None:
        return "dataset no evaluable"
    if not isinstance(documento.get("escenario_id"), str) or not documento["escenario_id"].strip():
        return "falta el identificador de escenario"
    if not isinstance(documento.get("evaluacion_id"), str) or not documento["evaluacion_id"].strip():
        return "falta el identificador de evaluación"
    if not _fecha(documento.get("emitido_en")):
        return "marca de tiempo inválida"
    if documento.get("modo") not in ("simulacion", "escenario_inicial"):
        return "modo no admitido"
    if documento.get("version_contrato") != "1.3.0":
        return "contrato no admitido"
    controles = documento.get("controles")
    if not isinstance(controles, dict):
        return "los controles deben ser un objeto"
    for nombre, valor in controles.items():
        if nombre not in entradas:
            return f"{nombre} no es una entrada sustituible"
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            return f"{nombre} no es un número"
    originales = documento.get("valores_originales")
    if originales is not None and not isinstance(originales, dict):
        return "los valores originales no tienen el formato esperado"
    if documento.get("origen_valores") != "simulado":
        return "el origen de los valores debe identificar la simulación"
    return None


def _entradas(dataset_id, pozo_id: str) -> tuple[dict | None, str | None]:
    """BES-jun conserva sus dos entradas. Otro expediente usa su controles.json."""
    if dataset_id == "BES-jun":
        return dict(ENTRADAS), None
    if not isinstance(dataset_id, str) or not dataset_id:
        return None, None
    from services.dataset_registry import obtener

    ficha = obtener(dataset_id)
    if ficha is None or not ficha.puede_evaluar:
        return None, None
    rotulos = {item.get("pozo_rotulo") for item in ficha.pozos()}
    if pozo_id not in rotulos:
        return None, "el pozo no pertenece a ese dataset"
    documento = ficha.leer_json("integracion/controles.json")
    if not isinstance(documento, dict):
        return {}, None
    admitidas = {}
    for control in documento.get("controles") or []:
        if isinstance(control, dict) and control.get("id") and control.get("rol", "entrada") == "entrada":
            admitidas[str(control["id"])] = str(control.get("unidad") or "")
    return admitidas, None


def _fecha(texto) -> bool:
    if not isinstance(texto, str):
        return False
    try:
        datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True
