"""Lectura de la serie diaria de RB-IA-2191. No escribe el .xlsx."""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

HASH_ORIGINAL = "908149f26e7560dc6bce75dc0268560e93a05d88b685218856b738dea39d9f08"
COLUMNAS = (
    "FECHA", "BFPD", "BWPD", "BOPD", "HZ", "P_Sensor", "H", "Sum", "BSW",
    "PWF", "Volt_m", "Amp_m", "API", "T_Yac", "GE_W", "P_cas", "Visco_f",
    "THP", "P_SUT", "Pbomba", "Eff_b", "Porc_Load", "Eff_m", "FP", "PIP",
)


def raiz_expediente() -> Path:
    return Path(__file__).resolve().parents[1]


def ruta_entrada() -> Path:
    return raiz_expediente() / "entrada" / "RB-IA-2191-Data.xlsx"


def huella(ruta: Path | None = None) -> str:
    archivo = ruta or ruta_entrada()
    return hashlib.sha256(archivo.read_bytes()).hexdigest()


def leer_serie(ruta: Path | None = None) -> list[dict]:
    """Devuelve 28 registros con valores almacenados (data_only)."""
    archivo = ruta or ruta_entrada()
    libro = load_workbook(archivo, data_only=True, read_only=True)
    try:
        if libro.sheetnames != ["Hoja1"]:
            raise ValueError("El libro de trabajo no tiene la hoja esperada.")
        hoja = libro["Hoja1"]
        filas_raw = list(hoja.iter_rows(values_only=True))
    finally:
        libro.close()
    if not filas_raw:
        raise ValueError("La hoja está vacía.")
    encabezados = tuple(filas_raw[0])
    if encabezados != COLUMNAS:
        raise ValueError("Los encabezados no coinciden con el original leído el 2026-10-28.")
    filas = []
    for valores in filas_raw[1:]:
        if valores[0] is None:
            continue
        registro = {}
        for nombre, valor in zip(encabezados, valores):
            if nombre == "FECHA":
                if not isinstance(valor, datetime):
                    raise ValueError("Una fecha no es datetime.")
                registro[nombre] = valor
            elif valor is None or valor == "":
                registro[nombre] = None
            else:
                registro[nombre] = valor
        filas.append(registro)
    return filas


def formulas_bopd(ruta: Path | None = None) -> list[str]:
    """Lista las expresiones de la columna BOPD (únicas fórmulas visibles)."""
    archivo = ruta or ruta_entrada()
    libro = load_workbook(archivo, data_only=False, read_only=True)
    try:
        hoja = libro["Hoja1"]
        expresiones = []
        for fila in range(2, (hoja.max_row or 1) + 1):
            celda = hoja.cell(fila, 4).value
            if isinstance(celda, str) and celda.startswith("="):
                expresiones.append(celda)
            elif celda is None and hoja.cell(fila, 1).value is None:
                break
            else:
                expresiones.append(str(celda))
    finally:
        libro.close()
    return expresiones


def dia_referencia(serie: list[dict] | None = None) -> dict:
    """Primer día de la serie, 2020-05-02."""
    filas = serie if serie is not None else leer_serie()
    if not filas:
        raise ValueError("La serie no tiene filas.")
    return filas[0]


def fecha_iso(valor: datetime) -> str:
    return valor.date().isoformat()
