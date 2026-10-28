"""Lee el bloque Measured de cada hoja. No guarda el libro ni imputa estaciones."""

from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook

from ingesta.leer_bes_jun import COPIA_TRABAJO


def leer_survey(ruta: Path | None = None) -> list[dict]:
    ruta = Path(ruta) if ruta is not None else COPIA_TRABAJO
    libro = load_workbook(ruta, data_only=True)
    try:
        filas = []
        for ws in libro.worksheets:
            encabezado = None
            for fila in range(1, (ws.max_row or 0) + 1):
                if ws.cell(fila, 1).value == "Measured":
                    encabezado = fila
                    break
            if encabezado is None:
                continue
            fila = encabezado + 1
            while fila <= (ws.max_row or 0):
                md = ws.cell(fila, 1).value
                if md in (None, ""):
                    break
                if isinstance(md, (int, float)):
                    filas.append(
                        {
                            "hoja": ws.title,
                            "md_ft": float(md),
                            "inclinacion_deg": _num(ws.cell(fila, 2).value),
                            "azimut_deg": _num(ws.cell(fila, 3).value),
                            "vertical_ft": _num(ws.cell(fila, 4).value),
                            "dogleg_deg_por_100ft": _num(ws.cell(fila, 5).value),
                        }
                    )
                fila += 1
        return filas
    finally:
        libro.close()


def _num(valor):
    if isinstance(valor, (int, float)):
        return float(valor)
    return None
