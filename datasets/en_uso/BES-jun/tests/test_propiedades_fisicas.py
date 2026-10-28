"""Consistencia matemática de las fórmulas transcritas.

Los valores esperados están escritos aquí. No salen de la función bajo prueba.
Reproducir la celda no se toma como validación física.
"""

import math

import pytest

from modelo_deterministico.balance_bes_jun import (
    friccion_hazen_williams_ft,
    pip_en_ft,
    thd_total_ft,
)
from modelo_deterministico.fluidos_bes_jun import (
    densidad_lb_por_galon,
    gradiente_psi_por_ft,
    gravedad_especifica_api,
)
from modelo_deterministico.hipotesis_ct03 import pip_ft_si_el_sensor_esta_mas_profundo
from modelo_deterministico.interseccion_bes_jun import caudal_a_producir, curva_a_velocidad


def test_api_10_es_gravedad_especifica_1_por_la_definicion():
    # 141.5 / (131.5 + 10) = 1. La identidad está escrita, no calculada por la función.
    assert gravedad_especifica_api(10) == pytest.approx(141.5 / 141.5)


def test_subir_el_api_baja_la_gravedad_especifica():
    assert gravedad_especifica_api(30) < gravedad_especifica_api(10)


def test_el_gradiente_es_el_factor_0_052_de_la_celda():
    # 8.34 lb/gal * 0.052 = 0.43368 psi/ft. Es el factor escrito, no una conversión nueva.
    assert gradiente_psi_por_ft(8.34) == pytest.approx(8.34 * 0.052)
    assert densidad_lb_por_galon(0.0, 8.34, 0.9) == pytest.approx(8.33 * 0.9)


def test_el_signo_de_la_celda_no_coincide_con_la_hidrostatica_simple():
    presion, intake, sensor, gradiente = 800.0, 2500.0, 2600.0, 0.4
    celda = pip_en_ft(presion, intake, sensor, gradiente)
    # Transcripción independiente: (P - (TVD_intake - TVD_sensor) * grad) / grad
    transcripcion = (presion - ((intake - sensor) * gradiente)) / gradiente
    hidrostatica = pip_ft_si_el_sensor_esta_mas_profundo(presion, intake, sensor, gradiente)
    assert celda == pytest.approx(transcripcion)
    assert hidrostatica == pytest.approx(presion / gradiente - (sensor - intake))
    assert celda != pytest.approx(hidrostatica)
    assert celda - hidrostatica == pytest.approx(2 * (sensor - intake))


def test_la_thd_cambia_con_el_signo_de_cada_termino():
    base = thd_total_ft(1000, 10, 20, 30)
    assert thd_total_ft(1001, 10, 20, 30) - base == pytest.approx(1)
    assert thd_total_ft(1000, 11, 20, 30) - base == pytest.approx(1)
    assert thd_total_ft(1000, 10, 21, 30) - base == pytest.approx(1)
    assert thd_total_ft(1000, 10, 20, 31) - base == pytest.approx(-1)


def test_la_friccion_de_la_hoja_tiene_los_exponentes_escritos():
    base = friccion_hazen_williams_ft(1000, 3, 2000)
    assert friccion_hazen_williams_ft(1000, 3, 4000) / base == pytest.approx(2)
    assert friccion_hazen_williams_ft(2000, 3, 2000) / base == pytest.approx(2**1.85)
    assert friccion_hazen_williams_ft(1000, 6, 2000) / base == pytest.approx((3 / 6) ** 4.8566)
    assert math.isfinite(base) and base > 0


def test_la_afinidad_de_la_hoja_escala_caudal_con_f_y_altura_con_f2():
    curva = [{"caudal_bfpd": 1000, "head_ft": 20}, {"caudal_bfpd": 2000, "head_ft": 10}]
    en_base = curva_a_velocidad(curva, 60, 60, 4)
    assert en_base[0]["caudal_bfpd"] == pytest.approx(1000)
    assert en_base[0]["head_ft"] == pytest.approx(20 * 4)
    al_doble = curva_a_velocidad(curva, 120, 60, 4)
    assert al_doble[0]["caudal_bfpd"] == pytest.approx(2000)
    assert al_doble[0]["head_ft"] == pytest.approx(20 * 4 * 4)


def test_sin_interseccion_no_se_extrapola():
    curva = [{"caudal_bfpd": 1000, "head_ft": 20}, {"caudal_bfpd": 2000, "head_ft": 10}]
    por_encima = caudal_a_producir(100, curva, 60, 60, 1)
    por_debajo = caudal_a_producir(5, curva, 60, 60, 1)
    assert por_encima.estado == "no_calculable"
    assert "fuera_de_curva_superior" in por_encima.alertas
    assert por_debajo.estado == "no_calculable"
    assert "fuera_de_curva_inferior" in por_debajo.alertas
    assert "caudal_a_producir_bfpd" not in por_encima.resultados
