"""Controles de calidad de los datos de BES-jun.

Cada control devuelve una evidencia verificable. Ninguno corrige datos.

Origen de cada criterio (para que no parezca un umbral inventado):
- «Regla de dominio»: la fórmula transcrita deja de tener sentido si no se cumple
  (p. ej. denominador cero, BS&W fuera de 0-1 en una fórmula que lo usa como fracción).
- «Geometría»: definición del survey (MD creciente; inclinación 0-180°; azimut 0-360°).
- «Observación»: se informa, no se juzga.
No se importan límites de operación de otras fuentes.
"""

from __future__ import annotations

import math

import numpy as np

TOLERANCIA_SURVEY_FT = 0.01  # una unidad del último decimal que muestra la hoja


def _arr(estaciones, clave):
    return np.array([e[clave] for e in estaciones], dtype=float)


def verificar_survey(estaciones: list[dict]) -> dict:
    """Propiedades geométricas básicas de una tabla de survey."""
    md, inc, az, tv = (_arr(estaciones, k) for k in ("md_ft", "inclinacion_deg", "azimut_deg", "vertical_ft"))
    return {
        "estaciones": len(estaciones),
        "md_inicial_ft": float(md[0]),
        "md_final_ft": float(md[-1]),
        "md_estrictamente_creciente": bool(np.all(np.diff(md) > 0)),
        "md_duplicadas": int(len(md) - len(set(md.tolist()))),
        "vertical_menor_o_igual_que_md": bool(np.all(tv <= md + 1e-9)),
        "vertical_monotona": bool(np.all(np.diff(tv) >= -1e-9)),
        "inclinacion_min_deg": float(inc.min()),
        "inclinacion_max_deg": float(inc.max()),
        "inclinacion_en_0_180": bool(inc.min() >= 0 and inc.max() <= 180),
        "azimut_en_0_360": bool(az.min() >= 0 and az.max() <= 360),
        "valores_nulos": int(sum(e[k] is None for e in estaciones for k in e if k != "hoja")),
    }


def curvatura_minima(md, inc_deg, az_deg) -> tuple[np.ndarray, np.ndarray]:
    """TVD acumulada y dogleg (°/100 ft) por el método de curvatura mínima.

    Método estándar de la industria, no una fórmula de este proyecto: se usa
    como control independiente de las columnas Vertical y Dogleg de la hoja.
    """
    md = np.asarray(md, dtype=float)
    inc = np.radians(np.asarray(inc_deg, dtype=float))
    az = np.radians(np.asarray(az_deg, dtype=float))
    tvd = np.zeros(len(md))
    dls = np.zeros(len(md))
    for i in range(1, len(md)):
        dmd = md[i] - md[i - 1]
        coseno = math.cos(inc[i] - inc[i - 1]) - math.sin(inc[i - 1]) * math.sin(inc[i]) * (
            1 - math.cos(az[i] - az[i - 1])
        )
        beta = math.acos(max(-1.0, min(1.0, coseno)))
        factor = 1.0 if beta < 1e-9 else (2.0 / beta) * math.tan(beta / 2.0)
        tvd[i] = tvd[i - 1] + (dmd / 2.0) * (math.cos(inc[i - 1]) + math.cos(inc[i])) * factor
        dls[i] = math.degrees(beta) / dmd * 100.0
    return tvd, dls


def contrastar_con_curvatura_minima(estaciones: list[dict]) -> dict:
    """Diferencia máxima entre las columnas de la hoja y el recálculo."""
    md, inc, az = (_arr(estaciones, k) for k in ("md_ft", "inclinacion_deg", "azimut_deg"))
    tv_hoja, dl_hoja = _arr(estaciones, "vertical_ft"), _arr(estaciones, "dogleg_deg_por_100ft")
    tv_calc, dl_calc = curvatura_minima(md, inc, az)
    d_tvd = float(np.max(np.abs(tv_calc - tv_hoja)))
    d_dls = float(np.max(np.abs(dl_calc[1:] - dl_hoja[1:])))
    return {
        "max_dif_tvd_ft": d_tvd,
        "max_dif_dogleg_deg_100ft": d_dls,
        "tolerancia": TOLERANCIA_SURVEY_FT,
        "coincide_dentro_del_redondeo": d_tvd <= TOLERANCIA_SURVEY_FT and d_dls <= TOLERANCIA_SURVEY_FT,
    }


def interpolar_tvd(estaciones: list[dict], md_ft: float) -> float | None:
    """TVD a una MD por interpolación lineal; None si la MD queda fuera del survey."""
    md, tv = _arr(estaciones, "md_ft"), _arr(estaciones, "vertical_ft")
    if md_ft is None or md_ft < md[0] or md_ft > md[-1]:
        return None
    return float(np.interp(md_ft, md, tv))


def verificar_tvd_de_equipos(hoja: dict, estaciones: list[dict]) -> list[dict]:
    """Compara TVD de descarga, intake y sensor con la interpolación del survey."""
    filas = []
    for equipo in ("descarga", "intake", "sensor"):
        md, tvd_hoja = hoja[f"md_{equipo}_ft"], hoja[f"tvd_{equipo}_ft"]
        tvd_calc = interpolar_tvd(estaciones, md)
        filas.append(
            {
                "hoja": hoja["hoja"],
                "equipo": equipo,
                "md_ft": md,
                "tvd_hoja_ft": tvd_hoja,
                "tvd_interpolada_ft": tvd_calc,
                "dif_ft": None if tvd_calc is None or tvd_hoja is None else tvd_calc - tvd_hoja,
                "dentro_del_survey": tvd_calc is not None,
                "tvd_menor_o_igual_que_md": None if tvd_hoja is None or md is None else tvd_hoja <= md,
            }
        )
    return filas


def plausibilidad_operacion(hoja: dict) -> list[dict]:
    """Comprobaciones de dominio y geometría sobre las entradas de una hoja."""

    def num(k):
        return hoja.get(k)

    def ok(valor, condicion):
        return None if valor is None else bool(condicion(valor))

    controles = [
        ("D-01", "dominio", "Caudal de operación >= 0", num("caudal_operacion_bfpd"), lambda v: v >= 0),
        ("D-02", "dominio", "Frecuencia de operación > 0", num("frecuencia_hz"), lambda v: v > 0),
        ("D-03", "dominio", "Presión de sensor > 0", num("presion_sensor_psi"), lambda v: v > 0),
        ("D-04", "dominio", "THP >= 0", num("thp_psi"), lambda v: v >= 0),
        ("D-05", "dominio", "°API > -131.5 (denominador de F-01)", num("api_deg"), lambda v: v > -131.5),
        (
            "D-06",
            "dominio",
            "BS&W entre 0 y 1 (la fórmula lo usa como fracción)",
            num("bsw_numero"),
            lambda v: 0 <= v <= 1,
        ),
        ("D-07", "dominio", "ID del tubing > 0", num("id_tubing_in"), lambda v: v > 0),
        ("D-08", "dominio", "Número de etapas > 0", num("etapas"), lambda v: v > 0),
        ("D-09", "dominio", "Frecuencia de la curva > 0", num("frecuencia_curva_hz"), lambda v: v > 0),
        (
            "G-01",
            "geometría",
            "TVD de descarga <= MD de descarga",
            None if None in (num("tvd_descarga_ft"), num("md_descarga_ft")) else (num("tvd_descarga_ft"), num("md_descarga_ft")),
            lambda v: v[0] <= v[1],
        ),
        (
            "G-02",
            "geometría",
            "MD descarga < MD intake < MD sensor (orden observado de la sarta)",
            None
            if None in (num("md_descarga_ft"), num("md_intake_ft"), num("md_sensor_ft"))
            else (num("md_descarga_ft"), num("md_intake_ft"), num("md_sensor_ft")),
            lambda v: v[0] < v[1] < v[2],
        ),
    ]
    filas = []
    for id_, tipo, descripcion, valor, condicion in controles:
        cumple = ok(valor, condicion)
        filas.append(
            {
                "hoja": hoja["hoja"],
                "control": id_,
                "tipo": tipo,
                "descripcion": descripcion,
                "valor": valor,
                "resultado": "no evaluable" if cumple is None else ("cumple" if cumple else "NO CUMPLE"),
            }
        )
    pb, ps = num("presion_burbuja_psi"), num("presion_sensor_psi")
    if pb is not None and ps is not None:
        filas.append(
            {
                "hoja": hoja["hoja"],
                "control": "O-01",
                "tipo": "observación",
                "descripcion": "Presión de sensor frente a presión de burbuja (la cadena de fluido no modela gas libre)",
                "valor": (ps, pb),
                "resultado": "sensor > burbuja" if ps > pb else "sensor <= burbuja",
            }
        )
    return filas
