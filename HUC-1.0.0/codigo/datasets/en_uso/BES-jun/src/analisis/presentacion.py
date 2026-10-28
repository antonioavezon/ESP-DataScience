"""Presentación de tablas en los cuadernos: sin índice, sin truncar textos, números legibles."""

from __future__ import annotations

import math

import pandas as pd


def _formato(valor):
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "—"
    if isinstance(valor, bool):
        return "sí" if valor else "no"
    if isinstance(valor, float):
        return f"{valor:.8g}"
    return str(valor)


def T(tabla: pd.DataFrame, ancha: bool = False):
    """Devuelve un Styler sin índice. ``ancha=True`` marca la tabla para página apaisada en el PDF."""
    clase = "tabla tabla-ancha" if ancha else "tabla"
    return (
        tabla.style.hide(axis="index")
        .format(_formato)
        .set_table_attributes(f'class="{clase}"')
    )
