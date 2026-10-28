"""El catastro cuadra con el código. No declara validada una ecuación para cerrar el informe."""

import json

import pytest

from analisis.calidad import curvatura_minima, interpolar_tvd
from analisis.sensibilidad_local import derivada_por_pie, elasticidad_relativa, q_estrella
from catalogo.catastro_formulas_bes_jun import (
    FORMULAS,
    funcion_importable,
    por_id,
    problemas_de_reconciliacion,
    resultados_de_hojas,
    resumen,
)
from ingesta.leer_bes_jun import leer_libro, raiz_expediente
from reglas.catalogo import REGLAS


def test_el_inventario_cuadra_y_no_repite_identificadores():
    assert problemas_de_reconciliacion() == []
    assert len({f["id"] for f in FORMULAS}) == len(FORMULAS)
    assert resumen()["principales_e01_a_e10"] == 10
    assert resumen()["validacion_externa_suficiente"] == 0


def test_cada_funcion_declarada_existe_y_la_prueba_cita_un_test():
    for formula in FORMULAS:
        if formula["funcion"]:
            assert callable(funcion_importable(formula)), formula["id"]
        if formula["consistencia_matematica"]:
            assert formula["prueba"]
            encontrado = any(
                formula["prueba"] in ruta.read_text(encoding="utf-8")
                for ruta in (raiz_expediente() / "tests").glob("test_*.py")
            )
            assert encontrado, formula["id"]


def test_e05_no_figura_como_validada_y_las_hipotesis_no_son_el_motor():
    e05 = por_id("E-05")
    assert e05["discrepancia_identificada"] is True
    assert e05["validacion_externa_suficiente"] is False
    assert e05["modelo_activo"] is True
    assert "discrepancia" in e05["estado_fisico"]
    assert por_id("HYP-CT03")["modelo_activo"] is False
    assert por_id("HYP-CT03")["utilizada_en_resultados"] is False
    assert por_id("HYP-PUNTO-FIJO")["funcion"] is None


def test_las_reglas_apuntan_a_formulas_o_a_ninguna():
    for regla in REGLAS:
        assert regla["aprobada_para_uso_operacional"] is False
        for dependencia in regla["ecuaciones_dependientes"]:
            assert por_id(dependencia)["id"] == "E-09"
    rc04 = next(r for r in REGLAS if r["id"] == "RC-BES-04")
    assert rc04["ecuaciones_dependientes"] == []
    assert rc04["estado_validacion"] == "no_evaluable"


def test_el_json_publicado_tiene_el_mismo_resumen_que_el_codigo():
    publicado = json.loads(
        (raiz_expediente() / "docs" / "catastro_maestro_formulas_BES-jun.json").read_text(encoding="utf-8")
    )
    assert publicado["resumen"] == resumen()
    assert len(publicado["formulas"]) == len(FORMULAS)
    assert "CT-03" in json.dumps(publicado["formulas"])


def test_los_cinco_pozos_conservan_la_regla_y_la_diferencia_de_pip():
    from ingesta.leer_bes_jun import leer_libro as _leer
    hojas = {h["pozo"]: h for h in _leer()}
    for fila in resultados_de_hojas():
        hoja = hojas[fila["pozo"]]
        assert fila["regla"] == "RC-BES-03"
        assert fila["diferencia_pip_celda_menos_hipotesis_ft"] == pytest.approx(
            2 * (hoja["tvd_sensor_ft"] - hoja["tvd_intake_ft"])
        )
        assert abs(fila["diferencia_q_estrella_menos_cache_bfpd"]) < 1e-6
    qf = next(f for f in resultados_de_hojas() if f["pozo"] == "QF-084")
    assert qf["limite_maximo_a_frecuencia_bfpd"] == pytest.approx(10500)


def test_aux_elasticidad_tiene_oraculo_independiente_de_la_combinacion():
    hoja = next(h for h in leer_libro() if h["pozo"] == "QF-084")
    delta = 0.01
    x = hoja["thp_psi"]
    q0 = q_estrella(hoja)
    qp = q_estrella({**hoja, "thp_psi": x * (1 + delta)})
    qm = q_estrella({**hoja, "thp_psi": x * (1 - delta)})
    esperado = (qp - qm) / (2 * delta * q0)
    assert elasticidad_relativa(hoja, "thp_psi")["elasticidad"] == pytest.approx(esperado)
    # Una respuesta lineal tiene elasticidad 1. Esa identidad no llama a la función de BES-jun.
    assert (12 - 8) / (2 * 0.2 * 10) == pytest.approx(1)


def test_aux_derivada_por_pie_tiene_oraculo():
    hoja = next(h for h in leer_libro() if h["pozo"] == "QF-084")
    paso = 1.0
    x = hoja["tvd_descarga_ft"]
    esperado = (
        q_estrella({**hoja, "tvd_descarga_ft": x + paso})
        - q_estrella({**hoja, "tvd_descarga_ft": x - paso})
    ) / (2 * paso)
    assert derivada_por_pie(hoja, "tvd_descarga_ft") == pytest.approx(esperado)


def test_aux_curvatura_minima_en_pozo_vertical():
    md = [0.0, 100.0, 250.0]
    inc = [0.0, 0.0, 0.0]
    az = [0.0, 0.0, 0.0]
    tvd, dogleg = curvatura_minima(md, inc, az)
    assert list(tvd) == pytest.approx(md)
    assert list(dogleg) == pytest.approx([0.0, 0.0, 0.0])


def test_aux_interpolacion_de_tvd():
    estaciones = [
        {"md_ft": 0.0, "vertical_ft": 0.0},
        {"md_ft": 100.0, "vertical_ft": 50.0},
    ]
    assert interpolar_tvd(estaciones, 50) == pytest.approx(25)
    assert interpolar_tvd(estaciones, 150) is None
