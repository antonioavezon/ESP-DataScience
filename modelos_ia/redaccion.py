"""Elige una sola respuesta visible. No calcula y no concatena el respaldo con el modelo."""

from __future__ import annotations

import re

_LETRAS = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúñÑ]")
_CIFRA = re.compile(r"\d+(?:[.,]\d+)?")
_PROHIBIDO = re.compile(
    r"sin riesgo|puedes aumentar|puede aumentar|está segura|esta segura|autorizo|"
    r"RC-BES|CT-0\d|contrato|evaluar_|ollama|traceback|d[oó]lar|bitcoin|"
    r"no hay en las hojas otro tipo|no aparece ningún otro tipo|no aparece ningun otro tipo",
    re.IGNORECASE,
)
# Token tras una cifra con mayúscula o barra: candidato a unidad (BFPD, Hz, psi/ft, BFP-DF…).
_UNIDAD_TRAS_CIFRA = re.compile(
    r"\d(?:[.,]\d+)?\s+((?=[\w/-]*[A-Z/])[A-Za-z°][\w°]*(?:[/-][\w°]+)*)"
)
_ROTULOS = ("NORMAL", "REGISTRO", "CRÍTICO", "CRITICO", "INCIPIENTE")


def elegir(respaldo: str, propuesto: str, corpus: str, rotulos: list[str], pozos: list[str]) -> str:
    """Devuelve el texto del modelo si respeta los hechos. Si no, el respaldo."""
    base = (respaldo or "").strip()
    if not base:
        base = "No hay un resultado consultable para esa pregunta."
    if not _aceptar(propuesto, corpus or base, rotulos, pozos):
        return base
    texto = propuesto.strip()
    if texto == base or texto in base or base in texto:
        return base
    return texto


def _aceptar(propuesto: str, corpus: str, rotulos: list[str], pozos: list[str]) -> bool:
    if not propuesto or not propuesto.strip() or not _LETRAS.search(propuesto):
        return False
    if _PROHIBIDO.search(propuesto):
        return False
    for hallada in _CIFRA.findall(propuesto):
        if not _presente(hallada, corpus) and not _presente(hallada.replace(",", "."), corpus):
            return False
    # La unidad que acompaña a una cifra debe existir tal cual en los hechos (p. ej. BFPD, Hz, psi/ft).
    for unidad in _UNIDAD_TRAS_CIFRA.findall(propuesto):
        if not re.search(rf"(?<![\w/-]){re.escape(unidad)}(?![\w/-])", corpus):
            return False
    esperados = {item.upper() for item in rotulos if item}
    for rotulo in _ROTULOS:
        if re.search(rf"\b{rotulo}\b", propuesto, re.IGNORECASE) and rotulo.upper() not in esperados and rotulo.upper().replace("Í", "I") not in {item.replace("Í", "I") for item in esperados}:
            if rotulo in ("CRITICO", "CRÍTICO") and any(item.replace("Í", "I") == "CRITICO" for item in esperados):
                continue
            return False
    mencionados = set(re.findall(r"QF-\d{3}|RB-\d{4}|RB-IA-\d+", propuesto, re.IGNORECASE))
    permitidos = {pozo.upper() for pozo in pozos}
    if mencionados and permitidos and not {item.upper() for item in mencionados} <= permitidos:
        return False
    return True


def _presente(cifra: str, corpus: str) -> bool:
    return re.search(rf"(?<!\d){re.escape(cifra)}(?!\d)", corpus) is not None
