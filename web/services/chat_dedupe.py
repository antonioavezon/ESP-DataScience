"""Elimina repeticiones textuales en respuestas del asistente.

No altera cifras: solo suprime frases o bloques que reiteran el mismo contenido.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

_SEP = re.compile(r"(?<=[.!?])\s+|\n+")
_NOISE = re.compile(r"[^\wáéíóúñüÁÉÍÓÚÑÜ]+", re.UNICODE)


def normalizar(texto: str) -> str:
    return _NOISE.sub(" ", (texto or "").casefold()).strip()


def tokens(texto: str) -> set[str]:
    return {t for t in normalizar(texto).split() if len(t) > 2}


def similitud(a: str, b: str) -> float:
    na, nb = normalizar(a), normalizar(b)
    if not na or not nb:
        return 0.0
    if na in nb or nb in na:
        return 1.0
    ta, tb = tokens(a), tokens(b)
    if ta and tb:
        jaccard = len(ta & tb) / len(ta | tb)
        if jaccard >= 0.72:
            return jaccard
    return SequenceMatcher(None, na, nb).ratio()


def frases(texto: str) -> list[str]:
    return [p.strip() for p in _SEP.split(texto or "") if p and p.strip()]


def dedupe_frases(texto: str, umbral: float = 0.86) -> str:
    """Quita oraciones duplicadas o casi duplicadas conservando el orden."""
    vistos: list[str] = []
    salida: list[str] = []
    for frase in frases(texto):
        if any(similitud(frase, previa) >= umbral for previa in vistos):
            continue
        vistos.append(frase)
        salida.append(frase)
    return " ".join(salida).strip()


def dedupe_parrafos(parrafos: list[str], umbral: float = 0.82) -> list[str]:
    vistos: list[str] = []
    salida: list[str] = []
    for raw in parrafos:
        texto = (raw or "").strip()
        if not texto:
            continue
        limpio = dedupe_frases(texto, umbral=0.9)
        if any(similitud(limpio, previa) >= umbral for previa in vistos):
            continue
        vistos.append(limpio)
        salida.append(limpio)
    return salida


def aporta_novedad(candidato: str, bases: list[str], umbral: float = 0.78) -> bool:
    """False si el candidato solo reitera lo ya dicho en bases."""
    cand = (candidato or "").strip()
    if not cand:
        return False
    if any(similitud(cand, base) >= umbral for base in bases if base):
        return False
    # Si casi todos los tokens del candidato ya están en las bases, no aporta.
    tc = tokens(cand)
    if not tc:
        return False
    union = set()
    for base in bases:
        union |= tokens(base)
    if union and len(tc & union) / len(tc) >= 0.9:
        return False
    return True
