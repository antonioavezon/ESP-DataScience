"""Impacto de las ambigüedades abiertas (CT-xx) sobre los resultados.

No decide cuál alternativa es correcta. Responde: si la alternativa fuera la
cierta, ¿cuánto cambiaría el resultado? Con eso se prioriza qué consulta
técnica es más urgente. No es una predicción ni una validación.
"""

from __future__ import annotations

from modelo_deterministico.balance_bes_jun import (
    friccion_hazen_williams_ft,
    pip_en_ft,
    thd_total_ft,
    thp_en_ft,
)
from modelo_deterministico.fluidos_bes_jun import (
    densidad_lb_por_galon,
    evaluar_fluido,
    gradiente_psi_por_ft,
)
from modelo_deterministico.interseccion_bes_jun import caudal_a_producir

EXPONENTE_PDF_004 = 4.8655  # página 2 del PDF 004-ESPdesign; la hoja usa 4.8566


def _cadena(h: dict, gradiente: float, *, signo_opuesto=False, exponente=None) -> dict:
    """PIP, THD y caudal a producir con las funciones transcritas.

    ``signo_opuesto`` intercambia TVD de intake y sensor dentro de la fórmula de PIP.
    """
    z_i, z_s = h["tvd_intake_ft"], h["tvd_sensor_ft"]
    if signo_opuesto:
        z_i, z_s = z_s, z_i
    pip = pip_en_ft(h["presion_sensor_psi"], z_i, z_s, gradiente)
    thp = thp_en_ft(h["thp_psi"], gradiente)
    kw = {} if exponente is None else {"exponente_id": exponente}
    fric = friccion_hazen_williams_ft(h["caudal_operacion_bfpd"], h["id_tubing_in"], h["tvd_descarga_ft"], **kw)
    thd = thd_total_ft(h["tvd_descarga_ft"], fric, thp, pip)
    q = caudal_a_producir(thd, h["curva"], h["frecuencia_hz"], h["frecuencia_curva_hz"], h["etapas"])
    return {
        "pip_ft": pip,
        "thd_ft": thd,
        "q_producir_bfpd": q.resultados["caudal_a_producir_bfpd"]["valor"] if q.estado == "calculable" else None,
        "estado_q": q.estado,
    }


def gradiente_base(h: dict) -> float:
    f = evaluar_fluido(h["api_deg"], h["temperatura_c"], h["bsw_numero"], h["densidad_agua_lb_gal"])
    return f.resultados["gradiente_psi_ft"]["valor"]


def tabla_de_impacto(h: dict) -> list[dict]:
    """Una fila por escenario alternativo, con la diferencia frente a la hoja."""
    g0 = gradiente_base(h)
    base = _cadena(h, g0)

    f = evaluar_fluido(h["api_deg"], h["temperatura_c"], h["bsw_numero"], h["densidad_agua_lb_gal"])
    sg60 = f.resultados["sg_60"]["valor"]
    rho_sin_t = densidad_lb_por_galon(h["bsw_numero"], h["densidad_agua_lb_gal"], sg60)
    g_sin_t = gradiente_psi_por_ft(rho_sin_t)

    escenarios = [
        ("CT-03", "Signo de PIP opuesto (analogía F-12)", _cadena(h, g0, signo_opuesto=True)),
        ("CT-05", "Exponente 4.8655 (PDF 004) en vez de 4.8566", _cadena(h, g0, exponente=EXPONENTE_PDF_004)),
        ("CT-04", "Sin corrección de temperatura de la gravedad", _cadena(h, g_sin_t)),
    ]
    filas = []
    for ct, descripcion, alt in escenarios:
        filas.append(
            {
                "hoja": h["hoja"],
                "consulta": ct,
                "escenario": descripcion,
                "pip_hoja_ft": base["pip_ft"],
                "pip_alt_ft": alt["pip_ft"],
                "d_pip_ft": alt["pip_ft"] - base["pip_ft"],
                "thd_hoja_ft": base["thd_ft"],
                "thd_alt_ft": alt["thd_ft"],
                "d_thd_ft": alt["thd_ft"] - base["thd_ft"],
                "q_hoja_bfpd": base["q_producir_bfpd"],
                "q_alt_bfpd": alt["q_producir_bfpd"],
                "d_q_bfpd": None
                if alt["q_producir_bfpd"] is None or base["q_producir_bfpd"] is None
                else alt["q_producir_bfpd"] - base["q_producir_bfpd"],
            }
        )
    return filas


def densidad_si_bsw_fuera_de_fraccion(h: dict) -> dict:
    """Densidad de mezcla si el número de BS&W se multiplicara tal cual como porcentaje.

    Prueba lógica de CT-02: ¿qué pasa si el número de la celda se interpretara
    como porcentaje (valor×100) dentro de la fórmula que lo usa como fracción?
    """
    f = evaluar_fluido(h["api_deg"], h["temperatura_c"], h["bsw_numero"], h["densidad_agua_lb_gal"])
    sg_t = f.resultados["sg_temperatura"]["valor"]
    rho_fraccion = densidad_lb_por_galon(h["bsw_numero"], h["densidad_agua_lb_gal"], sg_t)
    rho_porcentaje = densidad_lb_por_galon(h["bsw_numero"] * 100.0, h["densidad_agua_lb_gal"], sg_t)
    return {
        "hoja": h["hoja"],
        "bsw_celda": h["bsw_numero"],
        "densidad_como_fraccion_lb_gal": rho_fraccion,
        "densidad_si_se_usara_x100_lb_gal": rho_porcentaje,
        "densidad_agua_lb_gal": h["densidad_agua_lb_gal"],
        "x100_es_fisicamente_plausible": min(sg_t * 8.33, h["densidad_agua_lb_gal"]) * 0.9
        <= rho_porcentaje
        <= max(sg_t * 8.33, h["densidad_agua_lb_gal"]) * 1.1,
    }
