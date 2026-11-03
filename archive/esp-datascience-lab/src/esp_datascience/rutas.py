"""Localización del laboratorio y huella de archivos.

El texto de estas funciones es el de `notebooks/02_normalizacion.ipynb`.
"""

import hashlib
from pathlib import Path


def encontrar_raiz_laboratorio() -> Path:
    candidato = Path.cwd().resolve()
    for _ in range(6):
        mapping = candidato / "data" / "raw" / "mapping.xlsx"
        surging = candidato / "data" / "raw" / "surging.xlsx"
        if mapping.is_file() and surging.is_file():
            return candidato
        if candidato.parent == candidato:
            break
        candidato = candidato.parent
    raise FileNotFoundError(
        "No se encontró data/raw/mapping.xlsx junto a data/raw/surging.xlsx."
    )


def huella_sha256(ruta: Path) -> str:
    digest = hashlib.sha256()
    digest.update(ruta.read_bytes())
    return digest.hexdigest()
