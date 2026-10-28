"""Identidad de caudal que el libro declara en Excel.

BOPD = BFPD − BWPD

Es la única fórmula visible en la hoja. No usa BSW: en este archivo
BFPD × BSW no reproduce BWPD (diferencia máxima observada ≈ 64,44 BFPD).
No se importan las identidades de RB-1521 ni las reglas de BES-jun.
"""

from __future__ import annotations


def particionar(bfpd: float, bwpd: float) -> float:
    """Devuelve BOPD a partir de los caudales de fluidos y de agua."""
    return bfpd - bwpd


def identidad_exacta(fila: dict, tolerancia: float = 1e-9) -> bool:
    """True si BOPD almacenado coincide con BFPD − BWPD."""
    bfpd = fila.get("BFPD")
    bwpd = fila.get("BWPD")
    bopd = fila.get("BOPD")
    if not all(isinstance(valor, (int, float)) and not isinstance(valor, bool) for valor in (bfpd, bwpd, bopd)):
        return False
    return abs(particionar(float(bfpd), float(bwpd)) - float(bopd)) <= tolerancia


def bsw_reproduce_bwpd(fila: dict, tolerancia: float = 1e-6) -> bool:
    """Comprueba si BSW × BFPD reproduce BWPD. En este libro no cierra."""
    bfpd = fila.get("BFPD")
    bwpd = fila.get("BWPD")
    bsw = fila.get("BSW")
    if not all(isinstance(valor, (int, float)) and not isinstance(valor, bool) for valor in (bfpd, bwpd, bsw)):
        return False
    return abs(float(bfpd) * float(bsw) - float(bwpd)) <= tolerancia


def contar_identidades(serie: list[dict]) -> int:
    return sum(1 for fila in serie if identidad_exacta(fila))
