"""Valores operativos temporales por pozo. No escribe datasets."""

from __future__ import annotations

import threading

_CANDADO = threading.Lock()
_VALORES: dict[str, dict[str, float]] = {}


def obtener(pozo_id: str) -> dict[str, float] | None:
    with _CANDADO:
        ficha = _VALORES.get(pozo_id)
        return None if ficha is None else dict(ficha)


def guardar(pozo_id: str, valores: dict[str, float]) -> None:
    limpios = {
        str(clave): float(valor)
        for clave, valor in valores.items()
        if isinstance(valor, (int, float)) and not isinstance(valor, bool)
    }
    with _CANDADO:
        _VALORES[pozo_id] = limpios


def limpiar(pozo_id: str) -> None:
    with _CANDADO:
        _VALORES.pop(pozo_id, None)


def limpiar_todo() -> None:
    with _CANDADO:
        _VALORES.clear()


def activos() -> list[str]:
    with _CANDADO:
        return sorted(_VALORES.keys())
