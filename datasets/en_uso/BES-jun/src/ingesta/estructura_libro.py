"""Inventario estructural del libro BES-jun, solo lectura.

Describe cómo está construido el archivo (hojas, fórmulas, errores
cacheados, gráficos). No interpreta variables físicas.
"""

from __future__ import annotations

import re
import zipfile
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook

from ingesta.leer_bes_jun import COPIA_TRABAJO, _buscar_en_columna

_FUNCION = re.compile(r"([A-Z][A-Z0-9\.]+)\(")

# (nombre lógico, columna del rótulo, fila desde la que buscar)
ANCLAS = (
    ("Descarga (mecánica)", 1, 1, "Descarga"),
    ("Intake (mecánica)", 1, 1, "Intake"),
    ("Sensor (mecánica)", 1, 1, "Sensor"),
    ("Velocidad (operación)", 1, 60, "Velocidad"),
    ("Caudal (operación)", 1, 60, "Caudal"),
    ("Presión de Sensor", 1, 60, "Presión de Sensor"),
    ("PIP en (ft)", 5, 1, "PIP en (ft)"),
    ("THD TOTAL", 5, 1, "THD TOTAL"),
    ("Limite maximo", 5, 1, "Limite maximo"),
    ("Caudal a producir", 1, 60, "Caudal a producir"),
)


def inventario_zip(ruta: Path = COPIA_TRABAJO) -> dict:
    """Contenido del contenedor .xlsx (que es un ZIP)."""
    with zipfile.ZipFile(ruta) as z:
        nombres = z.namelist()
        corrupto = z.testzip()
    return {
        "entradas_zip": len(nombres),
        "hojas_xml": sum(n.startswith("xl/worksheets/sheet") for n in nombres),
        "graficos": sum(re.fullmatch(r"xl/charts/chart\d+\.xml", n) is not None for n in nombres),
        "imagenes": sum(n.startswith("xl/media/") for n in nombres),
        "tiene_macros_vba": any("vbaProject" in n for n in nombres),
        "tiene_enlaces_externos": any(n.startswith("xl/externalLinks/") for n in nombres),
        "tiene_cadena_de_calculo": "xl/calcChain.xml" in nombres,
        "primer_archivo_corrupto": corrupto,
    }


def inventario_hojas(ruta: Path = COPIA_TRABAJO) -> list[dict]:
    """Una fila por hoja: tamaño, celdas por tipo, funciones y errores cacheados."""
    wf = load_workbook(ruta, data_only=False)
    wv = load_workbook(ruta, data_only=True)
    try:
        filas = []
        for ws in wf.worksheets:
            v = wv[ws.title]
            formulas = constantes = 0
            funciones: Counter = Counter()
            hojas_citadas = 0
            for fila in ws.iter_rows():
                for c in fila:
                    if c.value is None:
                        continue
                    if isinstance(c.value, str) and c.value.startswith("="):
                        formulas += 1
                        funciones.update(_FUNCION.findall(c.value))
                        if "!" in c.value:
                            hojas_citadas += 1
                    else:
                        constantes += 1
            errores = sum(
                1
                for fila in v.iter_rows()
                for c in fila
                if isinstance(c.value, str) and c.value.startswith("#")
            )
            filas.append(
                {
                    "hoja": ws.title,
                    "estado": ws.sheet_state,
                    "dimension": ws.dimensions,
                    "filas": ws.max_row,
                    "columnas": ws.max_column,
                    "celdas_combinadas": len(ws.merged_cells.ranges),
                    "formulas": formulas,
                    "constantes": constantes,
                    "formulas_que_citan_otra_hoja": hojas_citadas,
                    "errores_en_cache": errores,
                    "funciones": ", ".join(f"{k}×{n}" for k, n in sorted(funciones.items())),
                }
            )
        return filas
    finally:
        wf.close()
        wv.close()


def errores_cacheados(ruta: Path = COPIA_TRABAJO) -> list[dict]:
    """Celdas cuyo valor guardado es un código de error de Excel (#DIV/0!, #N/A, ...)."""
    wf = load_workbook(ruta, data_only=False)
    wv = load_workbook(ruta, data_only=True)
    try:
        salida = []
        for ws in wv.worksheets:
            for fila in ws.iter_rows():
                for c in fila:
                    if isinstance(c.value, str) and c.value.startswith("#"):
                        salida.append(
                            {
                                "hoja": ws.title,
                                "celda": c.coordinate,
                                "valor_en_cache": c.value,
                                "formula": wf[ws.title][c.coordinate].value,
                            }
                        )
        return salida
    finally:
        wf.close()
        wv.close()


def anclas_por_hoja(ruta: Path = COPIA_TRABAJO) -> list[dict]:
    """Fila donde cae cada rótulo clave en cada hoja.

    Si el rótulo no aparece se informa None. Sirve para mostrar que las
    posiciones cambian entre hojas y por qué no se leen celdas por coordenada fija.
    """
    wb = load_workbook(ruta, data_only=False)
    try:
        filas = []
        for ws in wb.worksheets:
            fila = {"hoja": ws.title}
            for nombre, columna, desde, texto in ANCLAS:
                fila[nombre] = _buscar_en_columna(ws, columna, texto, desde=desde)
            filas.append(fila)
        return filas
    finally:
        wb.close()
