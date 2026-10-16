"""Lectura de celdas y de las franjas de mapping.

El texto de estas funciones es el de `notebooks/02_normalizacion.ipynb`.
"""

import math

import pandas as pd


def es_numero(valor) -> bool:
    if isinstance(valor, bool) or valor is None:
        return False
    if isinstance(valor, (int, float)):
        return not (isinstance(valor, float) and math.isnan(valor))
    return False


def filas_de_franja_mapping(tabla: pd.DataFrame) -> list[int]:
    filas = []
    for fila in range(len(tabla)):
        for columna in range(tabla.shape[1]):
            valor = tabla.iat[fila, columna]
            if isinstance(valor, str) and (valor == "Single Phase" or valor.startswith("Qgd=")):
                filas.append(fila)
                break
    return filas


def psep_de_hoja(hoja: str) -> int:
    if not hoja.endswith("psig"):
        raise ValueError("La hoja no nombra la presión en psig.")
    return int(hoja.removesuffix("psig"))
