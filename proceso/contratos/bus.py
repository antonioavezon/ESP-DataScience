"""Cliente MQTT local. El broker no guarda el historial de escenarios."""

from __future__ import annotations

import paho.mqtt.client as mqtt

from proceso.contratos.mensajes import HOST, PUERTO


def nuevo(client_id: str) -> mqtt.Client:
    return mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=client_id,
        protocol=mqtt.MQTTv311,
    )


def conectar(cliente: mqtt.Client) -> None:
    cliente.connect(HOST, PUERTO, keepalive=30)
