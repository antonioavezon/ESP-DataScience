"""Redondeo solo para la pantalla. No se usa antes del motor."""

from __future__ import annotations


def formato_visible(valor) -> str | None:
    if valor is None or isinstance(valor, bool):
        return None
    if not isinstance(valor, (int, float)):
        return None
    texto = f"{float(valor):.2f}"
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto
