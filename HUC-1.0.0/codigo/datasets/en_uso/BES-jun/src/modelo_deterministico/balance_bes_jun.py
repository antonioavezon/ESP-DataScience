"""Balance escrito en «Copia de FINAL BES-jun.xlsx».

Transcribe las celdas. No cambia signos ni el exponente de Hazen-Williams
para acercarlo al PDF de diseño.
"""

from __future__ import annotations

from modelo_deterministico.resultado import Resultado

# Exponente escrito en la celda de fricción de BES-jun (p. ej. QF-554H!G100).
# El PDF 004-ESPdesign, página 2, escribe 4.8655. No se unifican.
EXPONENTE_ID_HAZEN_BES_JUN = 4.8566
COEFICIENTE_HAZEN = 2.083
C_HAZEN_BES_JUN = 120.0


def pip_en_ft(
    presion_sensor_psi: float,
    tvd_intake_ft: float,
    tvd_sensor_ft: float,
    gradiente_psi_ft: float,
) -> float:
    """PIP en pies de columna, con el signo de la hoja.

    (P_sensor - ((TVD_intake - TVD_sensor) * gradiente)) / gradiente
    Fuente: QF-554H!G96 y la celda «PIP en (ft)» de cada hoja.
    """
    return (
        presion_sensor_psi - ((tvd_intake_ft - tvd_sensor_ft) * gradiente_psi_ft)
    ) / gradiente_psi_ft


def thp_en_ft(thp_psi: float, gradiente_psi_ft: float) -> float:
    """THP en pies = THP_psi / gradiente. Fuente: QF-554H!G98."""
    return thp_psi / gradiente_psi_ft


def friccion_hazen_williams_ft(
    caudal_bfpd: float,
    id_tubing_in: float,
    longitud_ft: float,
    c_hazen: float = C_HAZEN_BES_JUN,
    exponente_id: float = EXPONENTE_ID_HAZEN_BES_JUN,
) -> float:
    """Pérdida por fricción en ft, con las constantes de la celda BES-jun.

    (2.083 * (100/C)^1.85 * (Q/34.3)^1.85 * (1/ID^4.8566)) * (L/1000)
    C = 120 está escrito en la fórmula, no en una celda de entrada.
    L es la TVD de descarga que usa la hoja (QF-554H!C18), no la longitud medida del tubing.
    exponente_id solo se cambia en análisis de sensibilidad; el valor por defecto
    es el de la hoja.
    """
    factor = (
        COEFICIENTE_HAZEN
        * ((100.0 / c_hazen) ** 1.85)
        * ((caudal_bfpd / 34.3) ** 1.85)
        * (1.0 / (id_tubing_in**exponente_id))
    )
    return factor * (longitud_ft / 1000.0)


def thd_total_ft(
    tvd_descarga_ft: float,
    friccion_ft: float,
    thp_ft: float,
    pip_ft: float,
) -> float:
    """THD TOTAL = TVD_descarga + fricción + THP_ft - PIP_ft.

    Fuente: QF-554H!G102. La hoja lo llama THD TOTAL.
    No se afirma que sea el TDH del PDF (Pbdp + Pcf + nivel dinámico).
    """
    return tvd_descarga_ft + friccion_ft + thp_ft - pip_ft


def evaluar_balance(
    presion_sensor_psi: float | None,
    thp_psi: float | None,
    tvd_intake_ft: float | None,
    tvd_sensor_ft: float | None,
    tvd_descarga_ft: float | None,
    gradiente_psi_ft: float | None,
    caudal_bfpd: float | None,
    id_tubing_in: float | None,
) -> Resultado:
    """Evalúa PIP, THP en pies, fricción y THD, o devuelve no calculable."""
    entradas = {
        "presion_sensor_psi": {"valor": presion_sensor_psi, "unidad": "psi"},
        "thp_psi": {"valor": thp_psi, "unidad": "psi"},
        "tvd_intake_ft": {"valor": tvd_intake_ft, "unidad": "ft"},
        "tvd_sensor_ft": {"valor": tvd_sensor_ft, "unidad": "ft"},
        "tvd_descarga_ft": {"valor": tvd_descarga_ft, "unidad": "ft"},
        "gradiente_psi_ft": {"valor": gradiente_psi_ft, "unidad": "psi/ft"},
        "caudal_bfpd": {"valor": caudal_bfpd, "unidad": "BFPD"},
        "id_tubing_in": {"valor": id_tubing_in, "unidad": "in"},
    }
    faltan = [k for k, v in entradas.items() if v["valor"] is None]
    if faltan:
        return Resultado(
            estado="no_calculable",
            motivo="Faltan entradas esenciales del balance: " + ", ".join(faltan),
            entradas=entradas,
            ecuaciones=["BES-jun G96", "BES-jun G98", "BES-jun G100", "BES-jun G102"],
            alertas=["dato_faltante"],
        )
    if gradiente_psi_ft == 0 or id_tubing_in <= 0 or caudal_bfpd < 0 or tvd_descarga_ft < 0:
        return Resultado(
            estado="no_calculable",
            motivo="Gradiente nulo, diámetro no positivo, caudal negativo o TVD de descarga negativa.",
            entradas=entradas,
            alertas=["fuera_de_dominio"],
        )
    pip = pip_en_ft(presion_sensor_psi, tvd_intake_ft, tvd_sensor_ft, gradiente_psi_ft)
    thp = thp_en_ft(thp_psi, gradiente_psi_ft)
    fric = friccion_hazen_williams_ft(caudal_bfpd, id_tubing_in, tvd_descarga_ft)
    thd = thd_total_ft(tvd_descarga_ft, fric, thp, pip)
    advertencias = [
        "PIP en ft se calcula a partir de la presión de sensor y de las TVD; no es una estimación independiente del sensor.",
        "La fricción usa el exponente 4.8566 de la hoja, C=120 escrito en la fórmula y la TVD de descarga como longitud.",
        "Este resultado reproduce la planilla. No es una predicción validada contra una medición distinta de las entradas.",
    ]
    if pip < 0:
        advertencias.append("La fórmula devolvió PIP en ft negativo.")
    return Resultado(
        estado="calculable",
        motivo="Balance transcrito de la hoja BES-jun y evaluado con las entradas indicadas.",
        entradas=entradas,
        resultados={
            "pip_ft": {"valor": pip, "unidad": "ft", "formula": "BES-jun PIP en (ft)"},
            "thp_ft": {"valor": thp, "unidad": "ft", "formula": "BES-jun THP en (ft)"},
            "friccion_ft": {"valor": fric, "unidad": "ft", "formula": "BES-jun Hazen-Williams"},
            "thd_total_ft": {"valor": thd, "unidad": "ft", "formula": "BES-jun THD TOTAL"},
        },
        ecuaciones=["BES-jun G96", "BES-jun G98", "BES-jun G100", "BES-jun G102"],
        advertencias=advertencias,
    )
