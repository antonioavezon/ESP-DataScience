"""Sensibilidad local del caudal a producir a cada entrada, por diferencias centrales.

No es incertidumbre ni predicción: mide cuánto pesa cada entrada, alrededor del punto de operación de cada hoja,
en el resultado de la cadena transcrita. Cada perturbación recalcula toda la cadena con las funciones del contrato.
"""

from __future__ import annotations

from analisis.cadena import calcular_hoja

ENTRADAS_RELATIVAS = (
    "api_deg", "temperatura_c", "bsw_numero", "presion_sensor_psi", "thp_psi",
    "caudal_operacion_bfpd", "id_tubing_in", "tvd_descarga_ft", "frecuencia_hz", "etapas",
)
TVD_EQUIPOS = ("tvd_descarga_ft", "tvd_intake_ft", "tvd_sensor_ft")


def q_estrella(h: dict) -> float | None:
    """Caudal a producir de la hoja, o None si la cadena no es calculable."""
    q = calcular_hoja(h)["q"]
    if q.estado != "calculable":
        return None
    return q.resultados["caudal_a_producir_bfpd"]["valor"]


def _con(h: dict, clave: str, valor: float) -> dict:
    copia = dict(h)
    copia[clave] = valor
    return copia


def elasticidad_relativa(h: dict, clave: str, delta: float = 0.01) -> dict:
    """Elasticidad ε = (ΔQ*/Q*) / (Δx/x), con diferencia central y paso relativo ``delta``."""
    x = h[clave]
    q0 = q_estrella(h)
    qp = q_estrella(_con(h, clave, x * (1 + delta)))
    qm = q_estrella(_con(h, clave, x * (1 - delta)))
    if None in (q0, qp, qm):
        return {"clave": clave, "elasticidad": None, "dq_por_mas_1pct_bfpd": None}
    return {
        "clave": clave,
        "elasticidad": (qp - qm) / (2 * delta * q0),
        "dq_por_mas_1pct_bfpd": (qp - qm) / 2 * (0.01 / delta),
    }


def derivada_por_pie(h: dict, clave: str, paso_ft: float = 1.0) -> float | None:
    """dQ*/dTVD en BFPD por pie, con diferencia central de ``paso_ft`` pies."""
    x = h[clave]
    qp = q_estrella(_con(h, clave, x + paso_ft))
    qm = q_estrella(_con(h, clave, x - paso_ft))
    if qp is None or qm is None:
        return None
    return (qp - qm) / (2 * paso_ft)
