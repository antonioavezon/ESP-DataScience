"""Arma y valida escenarios. No ejecuta el motor ni escribe el Excel."""

from __future__ import annotations

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
WEB = RAIZ / "web"
for ruta in (RAIZ, WEB):
    if str(ruta) not in sys.path:
        sys.path.insert(0, str(ruta))


def _servicios():
    from services.escenario_inicial import escenario_de, listar_pozos, localizar

    return listar_pozos, localizar, escenario_de


def pozos() -> list[dict]:
    listar, _, _ = _servicios()
    return listar()


def base(pozo_id: str) -> dict | None:
    _, localizar, escenario_de = _servicios()
    encontrados = localizar(pozo_id)
    if len(encontrados) != 1:
        return None
    ficha, pozo = encontrados[0]
    escenario = escenario_de(pozo, ficha)
    return {
        "pozo_id": pozo_id,
        "dataset_id": escenario["dataset_id"],
        "evaluable": bool(escenario["evaluable"]),
        "hoja": escenario["hoja"],
        "version_contrato": "1.3.0",
        "controles": [
            {
                "id": control["id"],
                "nombre": control["nombre"],
                "unidad": control["unidad"],
                "valor_original": control["valor_inicial"],
                "recorrido": control["recorrido"],
            }
            for control in escenario["controles"]
        ],
    }


def validar(pozo_id: str, deseados: dict) -> tuple[dict | None, str | None]:
    ficha = base(pozo_id)
    if ficha is None:
        return None, "Ese pozo no está en el inventario."
    if not ficha["evaluable"]:
        return None, "Ese pozo no tiene motor. No se publica un escenario."
    if not isinstance(deseados, dict):
        return None, "Los valores tienen que ser un objeto."
    conocidos = {control["id"]: control for control in ficha["controles"]}
    cambios = {}
    for nombre, crudo in deseados.items():
        control = conocidos.get(nombre)
        if control is None:
            return None, f"{nombre} no es una entrada de este simulador."
        if isinstance(crudo, bool) or not isinstance(crudo, (int, float)):
            return None, f"{nombre} no es un número."
        valor = float(crudo)
        recorrido = control["recorrido"] or {}
        minimo = recorrido.get("minimo")
        maximo = recorrido.get("maximo")
        if minimo is None or maximo is None or valor < float(minimo) or valor > float(maximo):
            return None, f"{nombre} queda fuera del recorrido permitido."
        original = control["valor_original"]
        if original is None or abs(valor - float(original)) > 1e-6 * max(1.0, abs(float(original))):
            cambios[nombre] = valor
    return cambios, None


def mensaje(pozo_id: str, controles: dict, *, semilla: str | None = None, escenario_id: str | None = None) -> dict:
    ficha = base(pozo_id)
    originales = {control["id"]: control["valor_original"] for control in (ficha or {}).get("controles") or []}
    return {
        "version": "1",
        "origen": "data",
        "dataset_id": (ficha or {}).get("dataset_id") or "",
        "pozo_id": pozo_id,
        "escenario_id": escenario_id or f"esc-{pozo_id}-{uuid.uuid4().hex[:12]}",
        "evaluacion_id": f"ev-{uuid.uuid4().hex[:12]}",
        "emitido_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "modo": "simulacion" if controles else "escenario_inicial",
        "version_contrato": "1.3.0",
        "controles": controles,
        "valores_originales": originales,
        "origen_valores": "simulado",
        "semilla": semilla,
    }
