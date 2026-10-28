"""Ejecuta la cadena completa de una hoja (fluido, balance, intersección) con las funciones transcritas."""

from __future__ import annotations

from modelo_deterministico.balance_bes_jun import evaluar_balance
from modelo_deterministico.fluidos_bes_jun import evaluar_fluido
from modelo_deterministico.interseccion_bes_jun import caudal_a_producir


def calcular_hoja(h: dict) -> dict:
    """Devuelve {'fl': Resultado, 'ba': Resultado, 'q': Resultado} para una hoja leída por ``leer_libro``."""
    rf = evaluar_fluido(h["api_deg"], h["temperatura_c"], h["bsw_numero"], h["densidad_agua_lb_gal"])
    grad = rf.resultados["gradiente_psi_ft"]["valor"] if rf.estado == "calculable" else None
    rb = evaluar_balance(
        h["presion_sensor_psi"], h["thp_psi"], h["tvd_intake_ft"], h["tvd_sensor_ft"], h["tvd_descarga_ft"],
        grad, h["caudal_operacion_bfpd"], h["id_tubing_in"],
    )
    thd = rb.resultados["thd_total_ft"]["valor"] if rb.estado == "calculable" else None
    rq = caudal_a_producir(thd, h["curva"], h["frecuencia_hz"], h["frecuencia_curva_hz"], h["etapas"])
    return {"fl": rf, "ba": rb, "q": rq}
