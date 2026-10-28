"""Tres comprobaciones por ecuación. El valor esperado está escrito aquí.

El método B no llama a la función bajo prueba para construir el esperado.
Reproducir la caché de Excel no cuenta como el método C.
"""

import math

import pytest

from analisis.sensibilidad import gradiente_base
from ingesta.leer_bes_jun import leer_libro
from modelo_deterministico.balance_bes_jun import (
    friccion_hazen_williams_ft,
    pip_en_ft,
    thd_total_ft,
    thp_en_ft,
)
from modelo_deterministico.fluidos_bes_jun import (
    densidad_lb_por_galon,
    gradiente_psi_por_ft,
    gravedad_especifica_api,
    gravedad_oil_a_temperatura,
)
from modelo_deterministico.hipotesis_ct03 import pip_ft_si_el_sensor_esta_mas_profundo
from modelo_deterministico.interseccion_bes_jun import caudal_a_producir, curva_a_velocidad


def _sg_api(api):
    return 141.5 / (131.5 + api)


def _sg_temperatura(sg60, temperatura_c):
    delta = temperatura_c - 15.556
    return sg60 - 0.00066 * delta + 0.0000003 * delta * delta


def _densidad(bsw, rho_agua, sg_t):
    return bsw * rho_agua + (1.0 - bsw) * 8.33 * sg_t


def _pip_celda(presion, intake, sensor, gradiente):
    return (presion - ((intake - sensor) * gradiente)) / gradiente


def _pip_hidrostatica(presion, intake, sensor, gradiente):
    return presion / gradiente - (sensor - intake)


def _hazen(caudal, diametro, longitud, c=120.0, exponente=4.8566):
    factor = 2.083 * ((100.0 / c) ** 1.85) * ((caudal / 34.3) ** 1.85) / (diametro ** exponente)
    return factor * (longitud / 1000.0)


def _interpolar(q0, h0, q1, h1, thd):
    return q0 + (thd - h0) / (h1 - h0) * (q1 - q0)


def test_e01_definicion_oraculo_y_monotonia():
    # A. Definición API: 10 °API equivale a gravedad específica 1.
    assert _sg_api(10) == 1.0
    # B. Oráculo escrito arriba, no la función.
    assert gravedad_especifica_api(12) == pytest.approx(_sg_api(12))
    # C. Al subir °API la gravedad específica baja. No hay densidad medida de este crudo.
    assert gravedad_especifica_api(40) < gravedad_especifica_api(12)


def test_e02_coeficientes_de_la_celda_sin_origen_experimental():
    # A/B. La expresión y las constantes 0.00066, 0.0000003 y 15.556 están copiadas aquí.
    assert gravedad_oil_a_temperatura(0.9, 15.556) == pytest.approx(_sg_temperatura(0.9, 15.556))
    assert gravedad_oil_a_temperatura(0.9, 15.556) == pytest.approx(0.9)
    # C. Alrededor de 15.556 °C la pendiente escrita es -0.00066. No hay ensayo de este fluido.
    pendiente = (_sg_temperatura(0.9, 15.556 + 1.0) - _sg_temperatura(0.9, 15.556 - 1.0)) / 2
    assert pendiente == pytest.approx(-0.00066, abs=1e-6)
    assert gravedad_oil_a_temperatura(0.9, 80) < gravedad_oil_a_temperatura(0.9, 20)


def test_e03_mezcla_lineal_sin_convertir_el_rotulo_porcentual():
    # A/B. BSW = 0 es el petróleo; BSW = 1 es el agua. No se divide por 100.
    assert densidad_lb_por_galon(0.0, 8.34, 0.9) == pytest.approx(_densidad(0.0, 8.34, 0.9))
    assert densidad_lb_por_galon(1.0, 8.34, 0.9) == pytest.approx(8.34)
    assert densidad_lb_por_galon(0.0, 8.34, 0.9) == pytest.approx(8.33 * 0.9)
    # C. Con ambos componentes positivos, la mezcla en (0, 1) queda entre ellos.
    petroleo = _densidad(0.0, 8.34, 0.9)
    agua = _densidad(1.0, 8.34, 0.9)
    mezcla = densidad_lb_por_galon(0.4, 8.34, 0.9)
    assert min(petroleo, agua) < mezcla < max(petroleo, agua)


def test_e04_factor_0_052_y_contraste_con_el_sistema_internacional():
    # A/B. El factor de la celda está escrito: 8.34 * 0.052 = 0.43368.
    assert gradiente_psi_por_ft(8.34) == pytest.approx(8.34 * 0.052)
    assert 8.34 * 0.052 == pytest.approx(0.43368)
    # C. Constantes de conversión escritas aquí. No sustituyen el 0.052 de la hoja.
    lb_por_galon = 0.45359237 / 3.785411784 * 1000.0
    factor_si = lb_por_galon * 9.80665 * 0.3048 / 6894.757293168
    assert factor_si == pytest.approx(0.051948, abs=1e-5)
    assert abs(factor_si - 0.052) < 0.0001
    assert gradiente_psi_por_ft(8.34) != pytest.approx(8.34 * factor_si)


def test_e05_reproduccion_hidrostatica_y_cinco_pozos():
    # A/B. Transcripción independiente de G96.
    assert pip_en_ft(800, 2500, 2600, 0.4) == pytest.approx(_pip_celda(800, 2500, 2600, 0.4))
    # C. Con el sensor 100 ft más profundo, la diferencia algebraica es 200 ft.
    assert _pip_celda(800, 2500, 2600, 0.4) - _pip_hidrostatica(800, 2500, 2600, 0.4) == pytest.approx(200)
    assert pip_en_ft(800, 2500, 2600, 0.4) - pip_ft_si_el_sensor_esta_mas_profundo(800, 2500, 2600, 0.4) == pytest.approx(200)
    for hoja in leer_libro():
        gradiente = gradiente_base(hoja)
        celda = pip_en_ft(hoja["presion_sensor_psi"], hoja["tvd_intake_ft"], hoja["tvd_sensor_ft"], gradiente)
        hidro = _pip_hidrostatica(hoja["presion_sensor_psi"], hoja["tvd_intake_ft"], hoja["tvd_sensor_ft"], gradiente)
        separacion = hoja["tvd_sensor_ft"] - hoja["tvd_intake_ft"]
        assert separacion > 0
        assert celda - hidro == pytest.approx(2 * separacion)
        assert celda == pytest.approx(hoja["cache_pip_ft"], rel=1e-6)


def test_e06_presion_y_altura_son_inversas_del_gradiente():
    assert thp_en_ft(100, 0.4) == pytest.approx(100 / 0.4)
    assert thp_en_ft(200, 0.4) == pytest.approx(2 * thp_en_ft(100, 0.4))
    assert thp_en_ft(100, 0.8) == pytest.approx(0.5 * thp_en_ft(100, 0.4))


def test_e07_exponentes_de_la_hoja_no_el_pdf():
    base = _hazen(1000, 3, 5000)
    assert friccion_hazen_williams_ft(1000, 3, 5000) == pytest.approx(base)
    assert friccion_hazen_williams_ft(1000, 3, 10000) == pytest.approx(2 * base)
    assert friccion_hazen_williams_ft(2000, 3, 5000) == pytest.approx(base * (2 ** 1.85))
    assert friccion_hazen_williams_ft(1000, 6, 5000) == pytest.approx(base * (0.5 ** 4.8566))
    pdf = _hazen(1000, 3, 5000, exponente=4.8655)
    assert not math.isclose(base, pdf, rel_tol=1e-6)


def test_e08_el_balance_tiene_los_signos_escritos():
    assert thd_total_ft(1000, 10, 20, 30) == pytest.approx(1000 + 10 + 20 - 30)
    assert thd_total_ft(1001, 10, 20, 30) - thd_total_ft(1000, 10, 20, 30) == pytest.approx(1)
    assert thd_total_ft(1000, 11, 20, 30) - thd_total_ft(1000, 10, 20, 30) == pytest.approx(1)
    assert thd_total_ft(1000, 10, 21, 30) - thd_total_ft(1000, 10, 20, 30) == pytest.approx(1)
    assert thd_total_ft(1000, 10, 20, 31) - thd_total_ft(1000, 10, 20, 30) == pytest.approx(-1)


def test_e09_afinidad_con_una_razon_que_no_sale_del_dataset():
    puntos = [{"caudal_bfpd": 1000, "head_ft": 40}, {"caudal_bfpd": 2000, "head_ft": 10}]
    razon = 1.5
    escalada = curva_a_velocidad(puntos, 90, 60, 4)
    assert escalada[0]["caudal_bfpd"] == pytest.approx(1000 * razon)
    assert escalada[0]["head_ft"] == pytest.approx(40 * (razon ** 2) * 4)
    recuperada = curva_a_velocidad(escalada, 60, 90, 1 / 4)
    assert recuperada[0]["caudal_bfpd"] == pytest.approx(1000)
    assert recuperada[0]["head_ft"] == pytest.approx(40)
    identidad = curva_a_velocidad(puntos, 60, 60, 1)
    assert identidad[1]["head_ft"] == pytest.approx(10)


def test_e10_interpolacion_analitica_sin_extrapolacion():
    curva = [{"caudal_bfpd": 0, "head_ft": 100}, {"caudal_bfpd": 100, "head_ft": 0}]
    resultado = caudal_a_producir(50, curva, 60, 60, 1)
    assert resultado.estado == "calculable"
    assert resultado.resultados["caudal_a_producir_bfpd"]["valor"] == pytest.approx(_interpolar(0, 100, 100, 0, 50))
    assert caudal_a_producir(50, curva, 60, 60, 1).resultados["caudal_a_producir_bfpd"]["valor"] == pytest.approx(50)
    assert caudal_a_producir(150, curva, 60, 60, 1).estado == "no_calculable"
    assert caudal_a_producir(-1, curva, 60, 60, 1).estado == "no_calculable"
    # La fricción de la hoja depende del caudal medido. Dos caudales no dan la misma pérdida.
    assert friccion_hazen_williams_ft(1000, 3, 5000) != pytest.approx(friccion_hazen_williams_ft(2000, 3, 5000))
