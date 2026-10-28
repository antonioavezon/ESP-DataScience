"""Pruebas de la sensibilidad local (exactitud del método y signos físicos)."""

import pytest

from analisis.cadena import calcular_hoja
from analisis.sensibilidad_local import derivada_por_pie, elasticidad_relativa, q_estrella
from ingesta.leer_bes_jun import leer_libro
from modelo_deterministico.balance_bes_jun import friccion_hazen_williams_ft


@pytest.fixture(scope="module")
def hojas():
    return leer_libro()


def test_q_estrella_coincide_con_la_cadena(hojas):
    h = hojas[0]
    assert q_estrella(h) == calcular_hoja(h)["q"].resultados["caudal_a_producir_bfpd"]["valor"]


def test_el_metodo_recupera_el_exponente_exacto_de_la_friccion():
    # La fricción es ley de potencias: la elasticidad respecto de Q es 1.85 y respecto del ID es -4.8566.
    q, d, L = 8000.0, 2.996, 2600.0
    f0 = friccion_hazen_williams_ft(q, d, L)
    delta = 1e-6
    e_q = (friccion_hazen_williams_ft(q * (1 + delta), d, L) - friccion_hazen_williams_ft(q * (1 - delta), d, L)) / (2 * delta * f0)
    e_d = (friccion_hazen_williams_ft(q, d * (1 + delta), L) - friccion_hazen_williams_ft(q, d * (1 - delta), L)) / (2 * delta * f0)
    assert e_q == pytest.approx(1.85, abs=1e-6)
    assert e_d == pytest.approx(-4.8566, abs=1e-5)


def test_signos_fisicos_en_las_cinco_hojas(hojas):
    for h in hojas:
        assert elasticidad_relativa(h, "thp_psi")["elasticidad"] < 0          # más contrapresión, menos caudal
        assert elasticidad_relativa(h, "tvd_descarga_ft")["elasticidad"] < 0  # más altura que vencer, menos caudal
        assert elasticidad_relativa(h, "presion_sensor_psi")["elasticidad"] > 0  # más PIP, menos THD, más caudal
        assert elasticidad_relativa(h, "frecuencia_hz")["elasticidad"] > 0


def test_derivada_por_pie_finita_y_con_signo(hojas):
    for h in hojas:
        assert derivada_por_pie(h, "tvd_descarga_ft") < 0
