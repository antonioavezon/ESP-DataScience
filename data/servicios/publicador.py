"""Publica escenarios y recuerda el acuse. No interpreta la física."""

from __future__ import annotations

import json
import threading

from proceso.contratos.bus import conectar, nuevo
from proceso.contratos.mensajes import HOST, PUERTO, topic_escenario, topic_resultado

_ACUSES: dict[str, dict] = {}
_CANDADO = threading.Lock()
_CLIENTE = None
_LISTO = False


def acuse(evaluacion_id: str) -> dict | None:
    with _CANDADO:
        return _ACUSES.get(evaluacion_id)


def asegurar() -> str | None:
    global _CLIENTE, _LISTO
    if _LISTO:
        return None
    try:
        cliente = nuevo("huc-data")

        def al_conectar(cliente_mqtt, userdata, flags, reason_code, properties=None):
            cliente_mqtt.subscribe("huc/v1/proceso/+/resultado", qos=1)

        def al_mensaje(cliente_mqtt, userdata, mensaje):
            try:
                documento = json.loads(mensaje.payload.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                return
            if not isinstance(documento, dict):
                return
            identificador = documento.get("evaluacion_id")
            if isinstance(identificador, str):
                with _CANDADO:
                    _ACUSES[identificador] = {
                        "estado_publicacion": documento.get("estado_publicacion"),
                        "evaluacion_id": identificador,
                        "pozo_id": documento.get("pozo_id"),
                    }

        cliente.on_connect = al_conectar
        cliente.on_message = al_mensaje
        conectar(cliente)
        cliente.loop_start()
    except Exception as exc:
        return f"No hay broker MQTT en {HOST}:{PUERTO} ({exc.__class__.__name__})."
    _CLIENTE = cliente
    _LISTO = True
    return None


def publicar(documento: dict) -> str | None:
    error = asegurar()
    if error:
        return error
    from proceso.contratos.mensajes import validar_escenario

    detalle = validar_escenario(documento)
    if detalle:
        return detalle
    _CLIENTE.publish(topic_escenario(documento["pozo_id"]), json.dumps(documento, ensure_ascii=False), qos=1, retain=False)
    return None


def topic_de_resultado(pozo_id: str) -> str:
    return topic_resultado(pozo_id)
