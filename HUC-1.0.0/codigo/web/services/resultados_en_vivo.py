"""Último resultado publicado por PROCESO. No calcula."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone

_CANDADO = threading.Lock()
_RESULTADOS: dict[str, dict] = {}
_SERVICIO: dict[str, str | None] = {"emitido_en": None}
_HILO = False


def guardar(documento: dict) -> None:
    if not isinstance(documento, dict):
        return
    pozo = documento.get("pozo_id")
    if not isinstance(pozo, str) or not pozo:
        return
    with _CANDADO:
        previo = _RESULTADOS.get(pozo)
        if previo and _anterior(previo.get("emitido_en"), documento.get("emitido_en")):
            return
        _RESULTADOS[pozo] = documento


def guardar_servicio(documento: dict) -> None:
    if isinstance(documento, dict) and isinstance(documento.get("emitido_en"), str):
        with _CANDADO:
            _SERVICIO["emitido_en"] = documento["emitido_en"]


def ultimo(pozo_id: str) -> dict | None:
    with _CANDADO:
        documento = _RESULTADOS.get(pozo_id)
        return dict(documento) if documento else None


def filas(pozos: list[dict]) -> list[dict]:
    salida = []
    for pozo in pozos:
        identificador = pozo.get("pozo_id")
        documento = ultimo(identificador) if identificador else None
        if not documento:
            salida.append({
                "pozo_id": identificador,
                "codigo": "SIN_DATOS",
                "rotulo": "SIN RESULTADO",
                "tono": "sin-clasificacion",
                "clasificacion_valida": False,
                "origen": "sin_resultado",
                "fuente": "No hay un resultado publicado para este pozo.",
            })
            continue
        estado = documento.get("estado") if isinstance(documento.get("estado"), dict) else {}
        salida.append({
            "pozo_id": identificador,
            "codigo": estado.get("codigo") or "SIN_DATOS",
            "rotulo": estado.get("rotulo") or "SIN RESULTADO",
            "tono": estado.get("tono") or "sin-clasificacion",
            "clasificacion_valida": estado.get("clasificacion_valida") is True,
            "origen": documento.get("origen_valores") or "sin_resultado",
            "fuente": "Resultado publicado por el proceso.",
            "modo": documento.get("modo"),
        })
    return salida


def proceso_vigente(segundos: int = 15) -> bool:
    with _CANDADO:
        texto = _SERVICIO["emitido_en"]
    if not texto:
        return False
    try:
        momento = datetime.fromisoformat(texto)
    except ValueError:
        return False
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - momento).total_seconds() <= segundos


def _anterior(previo, nuevo) -> bool:
    if not isinstance(previo, str) or not isinstance(nuevo, str):
        return False
    return nuevo < previo


def arrancar() -> None:
    global _HILO
    if _HILO:
        return
    if os.environ.get("RUN_MAIN") not in (None, "", "true"):
        return
    if os.environ.get("RUN_MAIN") != "true" and os.environ.get("HUC_ENTORNO") != "contenedor":
        return
    _HILO = True
    hilo = threading.Thread(target=_escuchar, daemon=True)
    hilo.start()


def _escuchar() -> None:
    from proceso.contratos.bus import conectar, nuevo

    cliente = nuevo("huc-visualizacion")

    def al_conectar(cliente_mqtt, userdata, flags, reason_code, properties=None):
        cliente_mqtt.subscribe("huc/v1/proceso/+/resultado", qos=1)
        cliente_mqtt.subscribe("huc/v1/servicios/proceso/estado", qos=0)

    def al_mensaje(cliente_mqtt, userdata, mensaje):
        try:
            documento = json.loads(mensaje.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return
        if mensaje.topic.endswith("/estado") and mensaje.topic.startswith("huc/v1/servicios/"):
            guardar_servicio(documento)
            return
        guardar(documento)

    cliente.on_connect = al_conectar
    cliente.on_message = al_mensaje
    cliente.reconnect_delay_set(1, 30)
    while True:
        try:
            conectar(cliente)
            cliente.loop_forever()
        except Exception:
            time.sleep(2)
