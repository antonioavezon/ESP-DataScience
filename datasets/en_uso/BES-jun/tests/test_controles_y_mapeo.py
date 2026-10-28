"""Pruebas de los controles de integridad, calidad, mapeo, intersección y regla de caudal."""

import math

import pytest
from openpyxl import load_workbook

from analisis.calidad import (
    contrastar_con_curvatura_minima,
    plausibilidad_operacion,
    verificar_survey,
    verificar_tvd_de_equipos,
)
from analisis.criterios import Criterios
from analisis.dependencias import celdas_citadas, constantes_literales, firma_estructural, precedentes
from analisis.sensibilidad import tabla_de_impacto
from ingesta.estructura_libro import anclas_por_hoja, errores_cacheados, inventario_hojas, inventario_zip
from ingesta.integridad import comparar, control_negativo
from ingesta.leer_bes_jun import COPIA_TRABAJO, leer_libro
from ingesta.mapeo import VARIABLES, mapear
from ingesta.survey import leer_survey
from modelo_deterministico.balance_bes_jun import evaluar_balance, friccion_hazen_williams_ft
from modelo_deterministico.fluidos_bes_jun import evaluar_fluido
from modelo_deterministico.interseccion_bes_jun import caudal_a_producir
from reglas.candidatas_bes_jun import comparar_caudal_con_limites, limites_a_frecuencia


@pytest.fixture(scope="module")
def hojas():
    return leer_libro()


@pytest.fixture(scope="module")
def survey():
    return leer_survey()


def _thd(h):
    g = evaluar_fluido(h["api_deg"], h["temperatura_c"], h["bsw_numero"], h["densidad_agua_lb_gal"]).resultados[
        "gradiente_psi_ft"
    ]["valor"]
    b = evaluar_balance(
        h["presion_sensor_psi"], h["thp_psi"], h["tvd_intake_ft"], h["tvd_sensor_ft"],
        h["tvd_descarga_ft"], g, h["caudal_operacion_bfpd"], h["id_tubing_in"],
    )
    return b.resultados["thd_total_ft"]["valor"]


# --- integridad ---------------------------------------------------------------
def test_control_negativo_detecta_un_bit_cambiado():
    r = control_negativo(COPIA_TRABAJO)
    assert r["detecta_el_cambio"] and r["sha256_original"] != r["sha256_alterado"]


def test_una_ruta_ausente_no_aprueba_el_control(tmp_path):
    r = comparar({"a": COPIA_TRABAJO, "b": tmp_path / "no_existe.xlsx"})
    assert r["coincide"] is False and r["ausentes"] == ["b"]


def test_copias_identicas_coinciden(tmp_path):
    copia = tmp_path / "copia.xlsx"
    copia.write_bytes(COPIA_TRABAJO.read_bytes())
    assert comparar({"a": COPIA_TRABAJO, "b": copia})["coincide"] is True


# --- estructura ---------------------------------------------------------------
def test_estructura_del_libro():
    z = inventario_zip()
    assert z["graficos"] == 30 and not z["tiene_macros_vba"] and not z["tiene_enlaces_externos"]
    assert z["primer_archivo_corrupto"] is None
    filas = inventario_hojas()
    assert len(filas) == 5 and sum(f["formulas"] for f in filas) == 1270
    assert all(f["formulas_que_citan_otra_hoja"] == 0 for f in filas)


def test_trece_errores_cacheados_solo_en_qf_549hst():
    errores = errores_cacheados()
    assert len(errores) == 13 and {e["hoja"] for e in errores} == {"QF-549HST"}
    assert {e["valor_en_cache"] for e in errores} == {"#DIV/0!"}


def test_las_filas_de_los_bloques_cambian_entre_hojas():
    filas = {a["hoja"]: a["Caudal a producir"] for a in anclas_por_hoja()}
    assert len(set(filas.values())) > 1 and all(v is not None for v in filas.values())


# --- dependencias -------------------------------------------------------------
def test_celdas_citadas_expande_rangos_y_omite_texto():
    assert celdas_citadas("=B73-((C20-C24)*B102))/B102") == {"B73", "C20", "C24", "B102"}
    assert celdas_citadas("=INDEX(B86:B88,J95+1)") == {"B86", "B87", "B88", "J95"}
    assert celdas_citadas('=IF(G106>0,"Perdido A1",IF(G106<0,"Ganado"))') == {"G106"}
    assert celdas_citadas("=LOG10(A1)") == {"A1"}
    assert celdas_citadas("42") == set()


def test_los_errores_cacheados_no_son_precedentes_de_la_cadena():
    errores = {}
    for e in errores_cacheados():
        errores.setdefault(e["hoja"], set()).add(e["celda"])
    wb = load_workbook(COPIA_TRABAJO, data_only=False)
    try:
        for a in anclas_por_hoja():
            ws = wb[a["hoja"]]
            for nombre, celda in (("THD TOTAL", f"G{a['THD TOTAL']}"), ("Caudal a producir", f"B{a['Caudal a producir']}")):
                p = precedentes(ws, celda)
                assert not p["cita_otra_hoja"]
                assert not (p["formulas"] | p["constantes"]) & errores.get(a["hoja"], set()), (a["hoja"], nombre)
                assert len(p["formulas"]) > 3
    finally:
        wb.close()


# --- calidad del survey -------------------------------------------------------
def test_survey_geometria_y_curvatura_minima(hojas, survey):
    for h in hojas:
        est = [e for e in survey if e["hoja"] == h["hoja"]]
        v = verificar_survey(est)
        assert v["md_estrictamente_creciente"] and v["md_duplicadas"] == 0 and v["vertical_menor_o_igual_que_md"]
        assert v["inclinacion_en_0_180"] and v["azimut_en_0_360"] and v["valores_nulos"] == 0
        assert contrastar_con_curvatura_minima(est)["coincide_dentro_del_redondeo"]
        for fila in verificar_tvd_de_equipos(h, est):
            assert fila["dentro_del_survey"] and abs(fila["dif_ft"]) < 1e-6 and fila["tvd_menor_o_igual_que_md"]


def test_plausibilidad_no_marca_incumplimientos_en_los_datos_reales(hojas):
    for h in hojas:
        assert all(f["resultado"] != "NO CUMPLE" for f in plausibilidad_operacion(h))


def test_plausibilidad_detecta_un_bsw_en_porcentaje(hojas):
    malo = {**hojas[0], "bsw_numero": 97.55}
    assert any(f["control"] == "D-06" and f["resultado"] == "NO CUMPLE" for f in plausibilidad_operacion(malo))


# --- intersección sistema-bomba ----------------------------------------------
def test_caudal_a_producir_reproduce_la_cache_de_las_cinco_hojas(hojas):
    for h in hojas:
        r = caudal_a_producir(_thd(h), h["curva"], h["frecuencia_hz"], h["frecuencia_curva_hz"], h["etapas"])
        assert r.estado == "calculable"
        q = r.resultados["caudal_a_producir_bfpd"]["valor"]
        assert math.isclose(q, h["cache_caudal_producir_bfpd"], rel_tol=1e-9)


def test_caudal_a_producir_fuera_de_la_curva_no_es_calculable(hojas):
    h = hojas[0]
    args = (h["curva"], h["frecuencia_hz"], h["frecuencia_curva_hz"], h["etapas"])
    alta = caudal_a_producir(1e9, *args)
    baja = caudal_a_producir(-1.0, *args)
    assert alta.estado == "no_calculable" and "fuera_de_curva_superior" in alta.alertas
    assert baja.estado == "no_calculable" and "fuera_de_curva_inferior" in baja.alertas
    assert caudal_a_producir(None, *args).estado == "no_calculable"
    assert caudal_a_producir(2000.0, h["curva"], 0, 60, 10).estado == "no_calculable"


# --- regla de caudal con base de frecuencia ----------------------------------
def test_limites_se_escalan_con_f_sobre_60(hojas):
    h = hojas[0]
    lim = limites_a_frecuencia(h)
    assert math.isclose(lim["maximo_bfpd"], 10000 * 63 / 60) and math.isclose(lim["minimo_bfpd"], 2500 * 63 / 60)


def test_en_la_misma_base_de_frecuencia_las_cinco_hojas_estan_dentro(hojas):
    for h in hojas:
        r = comparar_caudal_con_limites(h)[0]
        assert r["id"] == "RC-BES-03" and r["estado_revision"] == "pendiente"


def test_la_comparacion_sin_escalar_produce_la_falsa_alarma_de_qf_084(hojas):
    por_pozo = {h["pozo"]: comparar_caudal_con_limites(h, escalar=False)[0] for h in hojas}
    assert por_pozo["QF-084"]["id"] == "RC-BES-01" and por_pozo["QF-084"]["umbral_bfpd"] == 10000
    assert sum(r["id"] == "RC-BES-01" for r in por_pozo.values()) == 1


# --- sensibilidad -------------------------------------------------------------
def test_signo_opuesto_de_pip_cambia_exactamente_dos_veces_la_diferencia_de_tvd(hojas):
    for h in hojas:
        fila = next(f for f in tabla_de_impacto(h) if f["consulta"] == "CT-03")
        esperado = -2.0 * (h["tvd_sensor_ft"] - h["tvd_intake_ft"])
        assert math.isclose(fila["d_pip_ft"], esperado, rel_tol=1e-9, abs_tol=1e-9)


def test_exponente_por_defecto_es_el_de_la_hoja(hojas):
    h = hojas[0]
    a = friccion_hazen_williams_ft(h["caudal_operacion_bfpd"], h["id_tubing_in"], h["tvd_descarga_ft"])
    b = friccion_hazen_williams_ft(h["caudal_operacion_bfpd"], h["id_tubing_in"], h["tvd_descarga_ft"], exponente_id=4.8566)
    assert a == b


# --- mapeo y criterios --------------------------------------------------------
def test_el_mapeo_coincide_con_el_lector(hojas):
    por_hoja = {h["hoja"]: h for h in hojas}
    filas = mapear()
    assert len(VARIABLES) == 34 and len(filas) == 5 * len(VARIABLES) and all(f["celda"] is not None for f in filas)
    for f in filas:
        ref = por_hoja[f["hoja"]].get(f["variable"])
        if ref is not None and isinstance(f["valor"], (int, float)):
            assert math.isclose(float(f["valor"]), ref, rel_tol=1e-12, abs_tol=1e-12), (f["hoja"], f["variable"])


def test_criterios_exigir_falla_si_un_criterio_no_se_cumple():
    c = Criterios("prueba")
    c.comprobar("X-1", "ok", True, "e")
    c.exigir()
    c.comprobar("X-2", "mal", False, "e")
    with pytest.raises(AssertionError):
        c.exigir()


# --- constantes y firma estructural ------------------------------------------
def test_constantes_literales_ignoran_referencias_y_funciones():
    f = "=(0.00066*(G30-15.556))+(0.0000003*((G30-15.556)^2))+LOG10(B2)+INDEX(B86:B91,J95+1)"
    assert constantes_literales(f) == [0.00066, 15.556, 0.0000003, 15.556, 2.0, 1.0]
    assert constantes_literales("=B73/B102") == []
    assert 4.8566 in constantes_literales("=(1/(B38)^4.8566)*(C18/1000)")


def test_la_firma_estructural_es_igual_en_las_cinco_hojas_para_la_cadena():
    from ingesta.leer_bes_jun import buscar_en_columna

    wb = load_workbook(COPIA_TRABAJO, data_only=False)
    try:
        cadena = [(1, "Gradiente de Presión", "B"), (5, "PIP en (ft)", "G"), (5, "THD TOTAL", "G"), (1, "Densidad de Fluido", "B")]
        for col, rotulo, letra in cadena:
            firmas = {firma_estructural(ws, f"{letra}{buscar_en_columna(ws, col, rotulo, desde=60 if col == 1 else 1)}") for ws in wb.worksheets}
            assert len(firmas) == 1, rotulo
    finally:
        wb.close()
