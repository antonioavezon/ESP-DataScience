"""Utilidades para construir los cuadernos del expediente con nbformat."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

from ingesta.leer_bes_jun import raiz_expediente

KERNEL = {"display_name": "Python (HUC VESP)", "language": "python", "name": "huc-vesp"}


def M(texto: str):
    return nbf.v4.new_markdown_cell(texto.strip("\n"))


def C(codigo: str):
    return nbf.v4.new_code_cell(codigo.strip("\n"))


PREPARACION = r"""
from pathlib import Path
import os, sys

def localizar_expediente() -> Path:
    # Sube desde el directorio actual hasta la carpeta que tiene dataset.md y entrada/.
    for p in [Path.cwd().resolve(), *Path.cwd().resolve().parents]:
        if (p / "dataset.md").is_file() and (p / "entrada").is_dir():
            return p
    raise RuntimeError("Ejecute el cuaderno dentro del expediente (donde están dataset.md y entrada/).")

RAIZ = localizar_expediente()                 # .../datasets/en_uso/BES-jun
RAIZ_PROYECTO = RAIZ.parents[2]               # .../HUC
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ / "src"))

import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 180)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.float_format", lambda v: f"{v:,.8g}")

from analisis.criterios import Criterios
from analisis.entorno import ficha
from analisis.presentacion import T
T(pd.DataFrame(list(ficha().items()), columns=["campo", "valor"]))
"""


def guardar(nombre: str, celdas: list) -> Path:
    from informes.cuadernos.cierres import CIERRES
    from informes.cuadernos.relacion_reglas import RELACION

    celdas = list(celdas)
    if nombre in RELACION:
        celdas.append(M("## Relación con el sistema de reglas\n\n" + RELACION[nombre]))
    if nombre in CIERRES:
        limitaciones, referencias = CIERRES[nombre]
        celdas.append(M("## Limitaciones\n\n" + limitaciones))
        celdas.append(M("## Referencias\n\nSolo se listan las fuentes realmente consultadas en este cuaderno.\n\n" + referencias))
    nb = nbf.v4.new_notebook()
    nb.cells = celdas
    nb.metadata["kernelspec"] = KERNEL
    nb.metadata["language_info"] = {"name": "python"}
    destino = raiz_expediente() / "notebooks" / f"{nombre}.ipynb"
    nbf.write(nb, destino)
    return destino
