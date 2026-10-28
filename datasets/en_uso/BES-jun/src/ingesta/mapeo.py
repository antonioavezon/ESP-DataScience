"""Mapeo de celdas de BES-jun a variables, con celda de origen, tipo y unidad rotulada.

Produce una tabla larga (una fila por hoja y variable). No convierte unidades
ni corrige valores: el número y el rótulo salen tal como están en la hoja.
La posición de cada celda se busca por rótulo, porque las filas cambian de una
hoja a otra.
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook

from ingesta.leer_bes_jun import COPIA_TRABAJO, _buscar_en_columna

# nombre, rótulo, col_rótulo, col_valor, col_unidad, desde, ocurrencia, rol
# col_unidad None: la unidad sale del encabezado de la tabla (se indica en 'unidad_fija').
VARIABLES = (
    ("frecuencia_hz", "Velocidad", 1, 2, 3, 60, 1, "entrada de operación"),
    ("caudal_operacion_bfpd", "Caudal", 1, 2, 3, 60, 1, "entrada de operación"),
    ("presion_sensor_psi", "Presión de Sensor", 1, 2, 3, 60, 1, "entrada de operación"),
    ("thp_psi", "THP", 1, 2, 3, 60, 1, "entrada de operación"),
    ("id_tubing_in", "ID", 1, 2, 3, 1, 1, "parámetro mecánico"),
    ("etapas", "Etapas", 1, 2, 3, 1, 1, "parámetro de bomba"),
    ("presion_yacimiento_psi", "Presión de Yacimiento", 5, 7, 8, 1, 1, "parámetro de yacimiento"),
    ("presion_burbuja_psi", "Presión de Burbuja", 5, 7, 8, 1, 1, "parámetro de fluido"),
    ("presion_prueba_psi", "Presión de Prueba", 5, 7, 8, 1, 1, "dato de prueba"),
    ("caudal_prueba_bfpd", "Caudal de Prueba", 5, 7, 8, 1, 1, "dato de prueba"),
    ("bsw_numero", "BS&W", 5, 7, 8, 1, 1, "parámetro de fluido"),
    ("temperatura_f", "Temperatura de fondo", 5, 7, 8, 1, 1, "parámetro de fluido"),
    ("temperatura_c", "Temperatura de fondo", 5, 7, 8, 1, 2, "calculada en la hoja"),
    ("api_deg", "API", 5, 7, 8, 1, 1, "parámetro de fluido"),
    ("densidad_agua_lb_gal", "Densidad del Agua", 5, 7, 8, 1, 1, "parámetro de fluido"),
    ("frecuencia_curva_hz", "Velocidad", 5, 7, 8, 1, 1, "referencia de la curva de bomba"),
    ("limite_minimo_bfpd", "Limite minimo", 5, 7, 8, 1, 1, "límite escrito en la hoja"),
    ("cono_eficiencia_bfpd", "Cono de eficiencia", 5, 7, 8, 1, 1, "límite escrito en la hoja"),
    ("limite_maximo_bfpd", "Limite maximo", 5, 7, 8, 1, 1, "límite escrito en la hoja"),
    ("md_descarga_ft", "Descarga", 1, 2, None, 1, 1, "parámetro mecánico"),
    ("tvd_descarga_ft", "Descarga", 1, 3, None, 1, 1, "calculada en la hoja"),
    ("md_intake_ft", "Intake", 1, 2, None, 1, 1, "parámetro mecánico"),
    ("tvd_intake_ft", "Intake", 1, 3, None, 1, 1, "calculada en la hoja"),
    ("md_sensor_ft", "Sensor", 1, 2, None, 1, 1, "parámetro mecánico"),
    ("tvd_sensor_ft", "Sensor", 1, 3, None, 1, 1, "calculada en la hoja"),
    ("cache_sg_60", "Gravedad Oil @ 60ºF", 1, 2, 3, 60, 1, "resultado de la hoja"),
    ("cache_sg_temperatura", "Gravedad Oil @ T fondo", 1, 2, 3, 60, 1, "resultado de la hoja"),
    ("cache_densidad_lb_gal", "Densidad de Fluido", 1, 2, 3, 60, 1, "resultado de la hoja"),
    ("cache_gradiente_psi_ft", "Gradiente de Presión", 1, 2, 3, 60, 1, "resultado de la hoja"),
    ("cache_pip_ft", "PIP en (ft)", 5, 7, 8, 1, 1, "resultado de la hoja"),
    ("cache_thp_ft", "THP en (ft)", 5, 7, 8, 1, 1, "resultado de la hoja"),
    ("cache_friccion_ft", "Perdidad por Fricción", 5, 7, 8, 1, 1, "resultado de la hoja"),
    ("cache_thd_ft", "THD TOTAL", 5, 7, 8, 1, 1, "resultado de la hoja"),
    ("cache_caudal_producir_bfpd", "Caudal a producir", 1, 2, 3, 60, 1, "resultado de la hoja"),
)

UNIDAD_ENCABEZADO = {2: "ft (encabezado «MD (ft)»)", 3: "ft (encabezado «TVD (ft)»)"}


def _fila(ws, rotulo, col, desde, ocurrencia):
    fila = _buscar_en_columna(ws, col, rotulo, desde=desde)
    for _ in range(ocurrencia - 1):
        if fila is None:
            return None
        fila = _buscar_en_columna(ws, col, rotulo, desde=fila + 1)
    return fila


def mapear(ruta: Path = COPIA_TRABAJO) -> list[dict]:
    """Tabla larga: hoja, variable, celda, tipo, fórmula, valor, unidad y rol."""
    wf = load_workbook(ruta, data_only=False)
    wv = load_workbook(ruta, data_only=True)
    try:
        salida = []
        for ws in wf.worksheets:
            v = wv[ws.title]
            for nombre, rotulo, c_rot, c_val, c_uni, desde, ocurr, rol in VARIABLES:
                fila = _fila(ws, rotulo, c_rot, desde, ocurr)
                if fila is None:
                    salida.append(
                        {"hoja": ws.title, "variable": nombre, "rotulo": rotulo, "celda": None,
                         "tipo_celda": "no encontrada", "formula": None, "valor": None,
                         "unidad_rotulada": None, "rol": rol}
                    )
                    continue
                crudo, cache = ws.cell(fila, c_val).value, v.cell(fila, c_val).value
                es_formula = isinstance(crudo, str) and crudo.startswith("=")
                valor = cache if es_formula else crudo
                unidad = UNIDAD_ENCABEZADO[c_val] if c_uni is None else ws.cell(fila, c_uni).value
                salida.append(
                    {
                        "hoja": ws.title,
                        "variable": nombre,
                        "rotulo": rotulo,
                        "celda": ws.cell(fila, c_val).coordinate,
                        "tipo_celda": "fórmula" if es_formula else "constante",
                        "formula": crudo if es_formula else None,
                        "valor": valor,
                        "unidad_rotulada": unidad,
                        "rol": rol,
                    }
                )
        return salida
    finally:
        wf.close()
        wv.close()
