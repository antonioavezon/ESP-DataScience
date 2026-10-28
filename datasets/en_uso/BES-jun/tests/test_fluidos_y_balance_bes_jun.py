"""Contrasta la transcripción con valores cacheados de BES-jun.

La coincidencia demuestra que el código repite la celda. No demuestra
que la celda haya sido validada contra un sensor independiente.
"""

import pytest

from ingesta.leer_bes_jun import COPIA_TRABAJO, leer_libro
from modelo_deterministico.balance_bes_jun import (
    evaluar_balance,
    friccion_hazen_williams_ft,
    pip_en_ft,
)
from modelo_deterministico.fluidos_bes_jun import (
    evaluar_fluido,
    gravedad_especifica_api,
)
from reglas.candidatas_bes_jun import comparar_caudal_con_limites

LIBRO = COPIA_TRABAJO


@pytest.fixture(scope="module")
def hojas():
    return leer_libro(LIBRO)


def test_f01_api_12_coincide_con_cache_de_la_hoja(hojas):
    esperado = 141.5 / (131.5 + 12)
    assert gravedad_especifica_api(12) == pytest.approx(esperado)
    assert gravedad_especifica_api(12) == pytest.approx(0.9860627177700348)
    assert all(h["api_deg"] == 12 for h in hojas)


def test_fluido_reproduce_gradiente_cacheado_en_las_cinco_hojas(hojas):
    for hoja in hojas:
        fluido = evaluar_fluido(
            hoja["api_deg"],
            hoja["temperatura_c"],
            hoja["bsw_numero"],
            hoja["densidad_agua_lb_gal"],
        )
        assert fluido.estado == "calculable"
        # El gradiente cacheado se recupera al rehacer la cadena, no al copiar la celda.
        balance = evaluar_balance(
            hoja["presion_sensor_psi"],
            hoja["thp_psi"],
            hoja["tvd_intake_ft"],
            hoja["tvd_sensor_ft"],
            hoja["tvd_descarga_ft"],
            fluido.resultados["gradiente_psi_ft"]["valor"],
            hoja["caudal_operacion_bfpd"],
            hoja["id_tubing_in"],
        )
        assert balance.estado == "calculable", hoja["llave"]
        assert balance.resultados["pip_ft"]["valor"] == pytest.approx(hoja["cache_pip_ft"], rel=1e-9)
        assert balance.resultados["thp_ft"]["valor"] == pytest.approx(hoja["cache_thp_ft"], rel=1e-9)
        assert balance.resultados["friccion_ft"]["valor"] == pytest.approx(
            hoja["cache_friccion_ft"], rel=1e-9
        )
        assert balance.resultados["thd_total_ft"]["valor"] == pytest.approx(
            hoja["cache_thd_ft"], rel=1e-9
        )


def test_signo_de_pip_es_el_de_la_celda_y_no_el_opuesto():
    # QF-554H: sensor más profundo que el intake. La celda suma esa diferencia.
    pip = pip_en_ft(732, 2653.176659090909, 2678.821959090909, 0.4334307341337953)
    assert pip == pytest.approx(1714.4964643339983, rel=1e-9)
    opuesto = (732 - ((2678.821959090909 - 2653.176659090909) * 0.4334307341337953)) / 0.4334307341337953
    assert pip != pytest.approx(opuesto, rel=1e-6)


def test_exponente_de_friccion_es_el_de_la_hoja_no_el_del_pdf():
    # Mismos datos de QF-554H. El PDF usa 4.8655; la hoja usa 4.8566.
    de_la_hoja = friccion_hazen_williams_ft(10301, 2.996, 2644.7774613636364)
    assert de_la_hoja == pytest.approx(730.7231971339377, rel=1e-6)


def test_dato_faltante_no_produce_numero():
    fluido = evaluar_fluido(12, 65.555, None, 8.345)
    assert fluido.estado == "no_calculable"
    assert fluido.resultados == {}
    balance = evaluar_balance(732, 183, 1, 2, 3, 0.43, None, 2.996)
    assert balance.estado == "no_calculable"
    assert "caudal_bfpd" in balance.motivo


def test_fuera_de_dominio_gradiente_cero_y_caudal_negativo():
    balance = evaluar_balance(732, 183, 100, 110, 90, 0.0, 1000, 2.996)
    assert balance.estado == "no_calculable"
    assert "fuera_de_dominio" in balance.alertas
    balance = evaluar_balance(732, 183, 100, 110, 90, 0.43, -1, 2.996)
    assert balance.estado == "no_calculable"


def test_cinco_hojas_cinco_pozos_distintos(hojas):
    assert len(hojas) == 5
    pozos = [h["pozo"] for h in hojas]
    assert pozos == ["QF-084", "QF-301", "QF-147", "QF-005", "QF-306"]
    assert len(set(pozos)) == 5
    assert all(h["cluster"] != h["pozo"] for h in hojas)


def test_regla_candidata_usa_el_limite_de_la_misma_hoja(hojas):
    # Los límites están a 60 Hz y la hoja los escala con f/60: la comparación válida
    # es en la misma base de frecuencia. La versión anterior de esta prueba exigía la
    # alerta de QF-084, que era un artefacto de comparar 63 Hz contra un límite a 60 Hz.
    por_pozo = {h["pozo"]: comparar_caudal_con_limites(h)[0] for h in hojas}
    assert por_pozo["QF-084"]["resultado"] == "dentro_de_los_limites_escritos"
    assert por_pozo["QF-084"]["limite_maximo_bfpd"] == pytest.approx(10500)
    assert por_pozo["QF-301"]["resultado"] == "dentro_de_los_limites_escritos"
    assert all(item["estado_revision"] == "pendiente" for item in por_pozo.values())
