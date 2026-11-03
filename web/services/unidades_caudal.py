"""Unidades canónicas de caudal para presentación.

BFPD, BWPD y BOPD comparten dimensión (barriles/día) pero no son intercambiables
como etiqueta: fluidos ≠ agua ≠ petróleo. No convierte valores numéricos.
"""

from __future__ import annotations

# Identificador de resultado/entrada → etiqueta de unidad que debe ver el operador.
UNIDAD_POR_ID = {
    "bfpd": "BFPD",
    "q_fluidos": "BFPD",
    "caudal_fluidos": "BFPD",
    "caudal_operacion_bfpd": "BFPD",
    "caudal_a_producir_bfpd": "BFPD",
    "bwpd": "BWPD",
    "q_water": "BWPD",
    "bopd": "BOPD",
    "q_oil": "BOPD",
}

DEFINICION_BFPD = (
    "BFPD = Barrels of Fluid Per Day: caudal total de fluidos, en barriles de fluido por día. "
    "No es BOPD (petróleo) ni BWPD (agua)."
)
DEFINICION_BWPD = (
    "BWPD = Barrels of Water Per Day: caudal de agua, en barriles de agua por día. "
    "No es BFPD (fluidos totales) ni BOPD (petróleo)."
)
DEFINICION_BOPD = (
    "BOPD = Barrels of Oil Per Day: caudal de petróleo, en barriles de petróleo por día. "
    "No es BFPD (fluidos totales) ni BWPD (agua)."
)


def unidad_de(identificador: str, unidad_publicada: str | None = None) -> str:
    """Devuelve la etiqueta canónica si el id es de caudal tipificado; si no, la publicada."""
    clave = (identificador or "").strip()
    if clave in UNIDAD_POR_ID:
        return UNIDAD_POR_ID[clave]
    return (unidad_publicada or "").strip()


def es_etiqueta_caudal_confusa(identificador: str, unidad: str) -> bool:
    """True si la unidad publicada contradice el significado del identificador."""
    esperada = UNIDAD_POR_ID.get(identificador)
    if not esperada:
        return False
    publicada = (unidad or "").strip().upper()
    return bool(publicada) and publicada != esperada
