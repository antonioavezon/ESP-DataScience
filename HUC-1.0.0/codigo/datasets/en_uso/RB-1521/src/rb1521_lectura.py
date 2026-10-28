"""Lectura de la serie diaria. No escribe el .xls."""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

import xlrd

HASH_ORIGINAL = "3c5043da6255c36c2c4270e465b4ee20dd7e6de534e58b8e84b42d350edf8808"
COLUMNAS = (
    "Fecha", "Q-fluidos", "Q-water", "Q-oil", "HZ", "P-sensor", "Nivel", "BSW",
    "PWf", "IP", "VOLT", "AMPs", "P-Yac", "PWf-test", "Pburbuja", "Q-test",
    "HZ-test", "Nivel-test", "Marca-Bomba", "API", "T-Yac", "GEP-Water", "P-cas",
    "Vel-fluidos", "T-tub", "D-tub", "N-sellos", "Z-intake", "Z-sensor", "Z-perf",
    "L-cable", "P-SUT",
)


def raiz_expediente() -> Path:
    return Path(__file__).resolve().parents[1]


def ruta_entrada() -> Path:
    return raiz_expediente() / "entrada" / "RB-1521-PY-121120.xls"


def huella(ruta: Path | None = None) -> str:
    archivo = ruta or ruta_entrada()
    return hashlib.sha256(archivo.read_bytes()).hexdigest()


def leer_serie(ruta: Path | None = None) -> list[dict]:
    """Devuelve 129 registros. Una celda vacía queda en None y no se convierte en cero."""
    archivo = ruta or ruta_entrada()
    libro = xlrd.open_workbook(archivo)
    if libro.nsheets != 1:
        raise ValueError("El libro de trabajo no tiene una sola hoja.")
    hoja = libro.sheet_by_index(0)
    encabezados = [hoja.cell_value(0, columna) for columna in range(hoja.ncols)]
    if tuple(encabezados) != COLUMNAS:
        raise ValueError("Los encabezados no coinciden con el original leído el 2026-10-28.")
    filas = []
    for fila in range(1, hoja.nrows):
        registro = {}
        for columna, nombre in enumerate(encabezados):
            celda = hoja.cell(fila, columna)
            if nombre == "Fecha":
                registro[nombre] = xlrd.xldate_as_datetime(celda.value, libro.datemode)
            elif celda.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) or celda.value == "":
                registro[nombre] = None
            else:
                registro[nombre] = celda.value
        filas.append(registro)
    return filas


def dia_referencia(serie: list[dict] | None = None) -> dict:
    """Primer día de la serie, 2020-05-02. En ese día la partición de caudal cierra."""
    filas = serie if serie is not None else leer_serie()
    if not filas:
        raise ValueError("La serie no tiene filas.")
    return filas[0]


def fecha_iso(valor: datetime) -> str:
    return valor.date().isoformat()
