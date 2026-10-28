"""Lee la copia de trabajo de BES-jun sin guardarla.

Localiza celdas por el texto del rótulo. No interpreta una columna
más allá de lo que el rótulo y la unidad escritos dicen.
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook


def raiz_expediente() -> Path:
    """Carpeta del expediente, la que contiene dataset.md y entrada/."""
    aqui = Path(__file__).resolve()
    for candidato in [aqui, *aqui.parents]:
        if (candidato / "dataset.md").is_file() and (candidato / "entrada").is_dir():
            return candidato
    raise RuntimeError("No se encontró el expediente (dataset.md y entrada/).")


COPIA_TRABAJO = raiz_expediente() / "entrada" / "BES_jun.xlsx"


def _texto(valor) -> str:
    if valor is None:
        return ""
    return str(valor).strip()


def _buscar_en_columna(ws, columna: int, texto: str, desde: int = 1):
    objetivo = texto.casefold()
    for fila in range(desde, ws.max_row + 1):
        if _texto(ws.cell(fila, columna).value).casefold() == objetivo:
            return fila
    return None


buscar_en_columna = _buscar_en_columna  # nombre público para otros módulos del expediente


def _numero(ws, wv, fila: int, columna: int):
    crudo = ws.cell(fila, columna).value
    cache = wv.cell(fila, columna).value
    if isinstance(cache, (int, float)):
        return float(cache)
    if isinstance(crudo, (int, float)):
        return float(crudo)
    return None


def _bloque_curva(ws):
    fila_unidad = _buscar_en_columna(ws, 5, "BFPD")
    if fila_unidad is None:
        return []
    puntos = []
    fila = fila_unidad + 1
    while fila <= ws.max_row:
        caudal = ws.cell(fila, 5).value
        head = ws.cell(fila, 6).value
        brake = ws.cell(fila, 7).value
        eff = ws.cell(fila, 8).value
        if not all(isinstance(v, (int, float)) for v in (caudal, head, brake, eff)):
            break
        puntos.append(
            {
                "caudal_bfpd": float(caudal),
                "head_ft": float(head),
                "brake_hp": float(brake),
                "eff_numero": float(eff),
                "eff_unidad_rotulo": "%",
            }
        )
        fila += 1
    return puntos


def leer_hoja(ws, wv) -> dict:
    """Extrae el punto de operación y los rótulos de una hoja."""
    fila_descarga = _buscar_en_columna(ws, 1, "Descarga")
    fila_intake = _buscar_en_columna(ws, 1, "Intake")
    fila_sensor_prof = _buscar_en_columna(ws, 1, "Sensor")
    fila_id = _buscar_en_columna(ws, 1, "ID")
    fila_ref = _buscar_en_columna(ws, 1, "Referencia")
    fila_etapas = _buscar_en_columna(ws, 1, "Etapas")

    fila_vel = _buscar_en_columna(ws, 1, "Velocidad", desde=60)
    fila_q = _buscar_en_columna(ws, 1, "Caudal", desde=60)
    fila_ps = _buscar_en_columna(ws, 1, "Presión de Sensor", desde=60)
    fila_thp = _buscar_en_columna(ws, 1, "THP", desde=60)

    def fila_e(texto: str):
        return _buscar_en_columna(ws, 5, texto)

    fila_api = fila_e("API")
    fila_bsw = fila_e("BS&W")
    fila_pr = fila_e("Presión de Yacimiento")
    fila_pb = fila_e("Presión de Burbuja")
    fila_t_c = None
    if fila_e("Temperatura de fondo") is not None:
        # La segunda aparición es la celda en °C, con fórmula.
        primera = fila_e("Temperatura de fondo")
        fila_t_c = _buscar_en_columna(ws, 5, "Temperatura de fondo", desde=primera + 1)
    fila_rho_w = fila_e("Densidad del Agua")
    fila_qprueba = fila_e("Caudal de Prueba")
    fila_pprueba = fila_e("Presión de Prueba")
    fila_frec_curva = fila_e("Velocidad")
    fila_qmin = fila_e("Limite minimo")
    fila_cono = fila_e("Cono de eficiencia")
    fila_qmax = fila_e("Limite maximo")
    fila_pip = fila_e("PIP en (ft)")
    fila_thp_ft = fila_e("THP en (ft)")
    fila_fric = fila_e("Perdidad por Fricción")
    fila_thd = fila_e("THD TOTAL")
    fila_q_producir = _buscar_en_columna(ws, 1, "Caudal a producir", desde=60)

    cluster = ws["B8"].value
    pozo = ws["B10"].value
    fecha_formula = ws["B6"].value
    fecha_cache = wv["B6"].value

    return {
        "hoja": ws.title,
        "estado_hoja": ws.sheet_state,
        "cluster": cluster,
        "pozo": pozo,
        "llave": f"{ws.title}|{pozo}",
        "fecha_formula": None if fecha_formula is None else str(fecha_formula),
        "fecha_cache": None if fecha_cache is None else str(fecha_cache),
        "fecha_es_today": isinstance(fecha_formula, str) and fecha_formula.replace("=", "").upper().startswith("TODAY"),
        "bomba_referencia": None if fila_ref is None else ws.cell(fila_ref, 2).value,
        "etapas": _numero(ws, wv, fila_etapas, 2) if fila_etapas else None,
        "id_tubing_in": _numero(ws, wv, fila_id, 2) if fila_id else None,
        "id_unidad_rotulo": None if fila_id is None else ws.cell(fila_id, 3).value,
        "frecuencia_hz": _numero(ws, wv, fila_vel, 2) if fila_vel else None,
        "caudal_operacion_bfpd": _numero(ws, wv, fila_q, 2) if fila_q else None,
        "presion_sensor_psi": _numero(ws, wv, fila_ps, 2) if fila_ps else None,
        "thp_psi": _numero(ws, wv, fila_thp, 2) if fila_thp else None,
        "api_deg": _numero(ws, wv, fila_api, 7) if fila_api else None,
        "bsw_numero": _numero(ws, wv, fila_bsw, 7) if fila_bsw else None,
        "bsw_unidad_rotulo": None if fila_bsw is None else ws.cell(fila_bsw, 8).value,
        "presion_yacimiento_psi": _numero(ws, wv, fila_pr, 7) if fila_pr else None,
        "presion_burbuja_psi": _numero(ws, wv, fila_pb, 7) if fila_pb else None,
        "temperatura_c": _numero(ws, wv, fila_t_c, 7) if fila_t_c else None,
        "densidad_agua_lb_gal": _numero(ws, wv, fila_rho_w, 7) if fila_rho_w else None,
        "caudal_prueba_bfpd": _numero(ws, wv, fila_qprueba, 7) if fila_qprueba else None,
        "presion_prueba_psi": _numero(ws, wv, fila_pprueba, 7) if fila_pprueba else None,
        "frecuencia_curva_hz": _numero(ws, wv, fila_frec_curva, 7) if fila_frec_curva else None,
        "limite_minimo_bfpd": _numero(ws, wv, fila_qmin, 7) if fila_qmin else None,
        "cono_eficiencia_bfpd": _numero(ws, wv, fila_cono, 7) if fila_cono else None,
        "limite_maximo_bfpd": _numero(ws, wv, fila_qmax, 7) if fila_qmax else None,
        "tvd_descarga_ft": _numero(ws, wv, fila_descarga, 3) if fila_descarga else None,
        "tvd_intake_ft": _numero(ws, wv, fila_intake, 3) if fila_intake else None,
        "tvd_sensor_ft": _numero(ws, wv, fila_sensor_prof, 3) if fila_sensor_prof else None,
        "md_descarga_ft": _numero(ws, wv, fila_descarga, 2) if fila_descarga else None,
        "md_intake_ft": _numero(ws, wv, fila_intake, 2) if fila_intake else None,
        "md_sensor_ft": _numero(ws, wv, fila_sensor_prof, 2) if fila_sensor_prof else None,
        "cache_pip_ft": _numero(ws, wv, fila_pip, 7) if fila_pip else None,
        "cache_thp_ft": _numero(ws, wv, fila_thp_ft, 7) if fila_thp_ft else None,
        "cache_friccion_ft": _numero(ws, wv, fila_fric, 7) if fila_fric else None,
        "cache_thd_ft": _numero(ws, wv, fila_thd, 7) if fila_thd else None,
        "cache_caudal_producir_bfpd": _numero(ws, wv, fila_q_producir, 2) if fila_q_producir else None,
        "curva": _bloque_curva(ws),
        "filas_usadas": ws.max_row,
        "columnas_usadas": ws.max_column,
    }


def leer_libro(ruta: Path | None = None) -> list[dict]:
    """Lee todas las hojas. Abre el libro dos veces y no lo guarda."""
    ruta = Path(ruta) if ruta is not None else COPIA_TRABAJO
    formulas = load_workbook(ruta, data_only=False)
    valores = load_workbook(ruta, data_only=True)
    try:
        hojas = []
        for nombre in formulas.sheetnames:
            hojas.append(leer_hoja(formulas[nombre], valores[nombre]))
        return hojas
    finally:
        formulas.close()
        valores.close()
