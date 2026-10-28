"""Secuencia reproducible dentro de los recorridos ya definidos."""

from __future__ import annotations

import random
import threading
import time

from data.simuladores.escenarios import base


class Secuencia:
    def __init__(self) -> None:
        self._candado = threading.Lock()
        self._estados: dict[str, dict] = {}

    def estado(self, pozo_id: str) -> str:
        with self._candado:
            ficha = self._estados.get(pozo_id)
            return "detenida" if ficha is None else ficha["fase"]

    def iniciar(self, pozo_id: str, intervalo_s: float, duracion_s: float, semilla: int, publicar) -> str | None:
        ficha = base(pozo_id)
        if ficha is None or not ficha["evaluable"]:
            return "Ese pozo no admite simulación automática."
        if intervalo_s < 0.2 or duracion_s < intervalo_s or duracion_s > 3600:
            return "El intervalo o la duración no son válidos."
        self.detener(pozo_id)
        pausa = threading.Event()
        alto = threading.Event()
        with self._candado:
            self._estados[pozo_id] = {"fase": "en_curso", "semilla": semilla, "pausa": pausa, "alto": alto}
        hilo = threading.Thread(
            target=self._correr,
            args=(pozo_id, intervalo_s, duracion_s, semilla, publicar, pausa, alto),
            daemon=True,
        )
        hilo.start()
        return None

    def pausar(self, pozo_id: str) -> None:
        with self._candado:
            ficha = self._estados.get(pozo_id)
            if ficha and ficha["fase"] == "en_curso":
                ficha["pausa"].set()
                ficha["fase"] = "en_pausa"

    def reanudar(self, pozo_id: str) -> None:
        with self._candado:
            ficha = self._estados.get(pozo_id)
            if ficha and ficha["fase"] == "en_pausa":
                ficha["pausa"].clear()
                ficha["fase"] = "en_curso"

    def detener(self, pozo_id: str) -> None:
        with self._candado:
            ficha = self._estados.pop(pozo_id, None)
        if ficha:
            ficha["alto"].set()
            ficha["pausa"].clear()

    def _correr(self, pozo_id, intervalo_s, duracion_s, semilla, publicar, pausa, alto) -> None:
        azar = random.Random(semilla)
        limite = time.monotonic() + duracion_s
        paso = 0
        while time.monotonic() < limite and not alto.is_set():
            if pausa.is_set():
                time.sleep(0.1)
                continue
            ficha = base(pozo_id)
            if not ficha:
                break
            valores = {}
            for control in ficha["controles"]:
                recorrido = control["recorrido"] or {}
                minimo = float(recorrido["minimo"])
                maximo = float(recorrido["maximo"])
                valores[control["id"]] = round(azar.uniform(minimo, maximo), 4)
            publicar(pozo_id, valores, f"{semilla}:{paso}")
            paso += 1
            time.sleep(intervalo_s)
        with self._candado:
            if self._estados.get(pozo_id, {}).get("alto") is alto:
                self._estados.pop(pozo_id, None)
