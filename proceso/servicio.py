"""Arranque del procesamiento. No abre una interfaz web."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from proceso.contratos.bus import conectar, nuevo
from proceso.contratos.mensajes import topic_escenario
from proceso.servicios.nodo import atender, latido, linea_base


def main() -> None:
    cliente = nuevo("huc-proceso")

    def al_conectar(cliente_mqtt, userdata, flags, reason_code, properties=None):
        cliente_mqtt.subscribe("huc/v1/data/+/escenario", qos=1)
        latido(cliente_mqtt)
        linea_base(cliente_mqtt)

    def al_mensaje(cliente_mqtt, userdata, mensaje):
        try:
            documento = json.loads(mensaje.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return
        esperado = None
        try:
            if isinstance(documento, dict) and isinstance(documento.get("pozo_id"), str):
                esperado = topic_escenario(documento["pozo_id"])
        except ValueError:
            return
        if mensaje.topic != esperado:
            return
        atender(cliente_mqtt, documento)

    cliente.on_connect = al_conectar
    cliente.on_message = al_mensaje
    cliente.reconnect_delay_set(1, 30)
    while True:
        try:
            conectar(cliente)
            break
        except Exception:
            time.sleep(2)
    cliente.loop_start()
    try:
        while True:
            latido(cliente)
            time.sleep(5)
    except KeyboardInterrupt:
        cliente.loop_stop()
        cliente.disconnect()


if __name__ == "__main__":
    main()
