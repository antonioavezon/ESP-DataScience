"""Orden de la curva de simulación. El caudal creciente es el contrato de esta representación.

La curva original de las cinco hojas no se reordena ni se modifica.
"""

import math

import pytest

from evaluacion.contratos import VERSION_CONTRATO, errores_de_salida
from evaluacion.motor import evaluar_solicitud
from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO, leer_libro
from modelo_deterministico.interseccion_bes_jun import caudal_a_producir


def _solicitud(curva, **extra):
    escenario = {"curva": curva}
    escenario.update(extra)
    return {
        "dataset_id": "BES-jun",
        "pozo_id": "QF-084",
        "version_configuracion": VERSION_CONTRATO,
        "modo": "simulacion",
        "escenario_id": "orden-curva",
        "variables": [],
        "parametros_escenario": escenario,
    }


@pytest.fixture(scope="module")
def hojas():
    return leer_libro()


def _rechazo(hojas, monkeypatch, curva, campo_fragmento):
    monkeypatch.setattr(
        "evaluacion.motor.calcular_hoja",
        lambda _hoja: (_ for _ in ()).throw(AssertionError("no calcular")),
    )
    resultado = evaluar_solicitud(_solicitud(curva), hojas=hojas)
    assert resultado["estado_evaluacion"] == "entrada_invalida"
    assert resultado["modelos"] == []
    assert resultado["reglas_ejecutadas"] == 0
    assert resultado["recomendacion_operacional_autorizada"] is False
    assert any(campo_fragmento in e["campo"] and e["codigo"] == "ESTRUCTURA_INVALIDA" for e in resultado["errores"])
    assert errores_de_salida(resultado) == []
    return resultado


def test_el_retroceso_de_caudal_no_llega_al_modelo(hojas, monkeypatch):
    curva = [
        {"caudal_bfpd": 0, "head_ft": 100},
        {"caudal_bfpd": 200, "head_ft": 50},
        {"caudal_bfpd": 100, "head_ft": 0},
    ]
    resultado = _rechazo(hojas, monkeypatch, curva, "curva[2].caudal_bfpd")
    assert any("estrictamente creciente" in e["detalle"] for e in resultado["errores"])


def test_el_caudal_decreciente_se_rechaza(hojas, monkeypatch):
    curva = [
        {"caudal_bfpd": 300, "head_ft": 90},
        {"caudal_bfpd": 200, "head_ft": 40},
        {"caudal_bfpd": 100, "head_ft": 10},
    ]
    _rechazo(hojas, monkeypatch, curva, "curva[1].caudal_bfpd")


def test_el_caudal_duplicado_senala_el_punto(hojas, monkeypatch):
    curva = [
        {"caudal_bfpd": 0, "head_ft": 80},
        {"caudal_bfpd": 100, "head_ft": 40},
        {"caudal_bfpd": 100, "head_ft": 10},
    ]
    resultado = _rechazo(hojas, monkeypatch, curva, "curva[2].caudal_bfpd")
    assert any("igual" in e["detalle"] for e in resultado["errores"])


def test_el_head_no_descendente_senala_su_campo(hojas, monkeypatch):
    curva = [
        {"caudal_bfpd": 0, "head_ft": 10},
        {"caudal_bfpd": 100, "head_ft": 40},
    ]
    resultado = _rechazo(hojas, monkeypatch, curva, "curva[1].head_ft")
    assert any("head" in e["detalle"].casefold() for e in resultado["errores"])


def test_caudal_y_head_invalidos_se_informan_juntos(hojas, monkeypatch):
    curva = [
        {"caudal_bfpd": 100, "head_ft": 10},
        {"caudal_bfpd": 50, "head_ft": 40},
    ]
    resultado = _rechazo(hojas, monkeypatch, curva, "curva[1]")
    campos = {e["campo"] for e in resultado["errores"]}
    assert any(c.endswith("caudal_bfpd") for c in campos)
    assert any(c.endswith("head_ft") for c in campos)


def test_valores_muy_proximos_se_aceptan_si_la_comparacion_exacta_crece(hojas):
    primero = 1000.0
    siguiente = math.nextafter(primero, math.inf)
    assert siguiente > primero
    curva = [
        {"caudal_bfpd": primero, "head_ft": 50},
        {"caudal_bfpd": siguiente, "head_ft": 49},
    ]
    resultado = evaluar_solicitud(_solicitud(curva, etapas={"valor": 1, "unidad": "1"}), hojas=hojas)
    assert resultado["estado_evaluacion"] != "entrada_invalida"
    assert resultado["errores"] == []
    assert resultado["recomendacion_operacional_autorizada"] is False


def test_muchos_puntos_validos_no_son_un_error_estructural(hojas):
    curva = [{"caudal_bfpd": float(i), "head_ft": float(80 - i)} for i in range(60)]
    resultado = evaluar_solicitud(_solicitud(curva, etapas={"valor": 1, "unidad": "1"}), hojas=hojas)
    assert resultado["estado_evaluacion"] != "entrada_invalida"
    assert resultado["errores"] == []


def test_una_curva_valida_sin_interseccion_es_no_evaluable(hojas):
    curva = [
        {"caudal_bfpd": 0, "head_ft": 100},
        {"caudal_bfpd": 500, "head_ft": 0},
    ]
    original = [dict(p) for p in next(h for h in hojas if h["pozo"] == "QF-084")["curva"]]
    antes = huellas(COPIA_TRABAJO)["sha256"]
    resultado = evaluar_solicitud(_solicitud(curva, etapas={"valor": 1, "unidad": "1"}), hojas=hojas)
    assert resultado["estado_evaluacion"] == "no_evaluable"
    assert resultado["modelos"]
    assert resultado["reglas_ejecutadas"] == 0
    assert resultado["recomendacion_operacional_autorizada"] is False
    assert errores_de_salida(resultado) == []
    assert next(h for h in hojas if h["pozo"] == "QF-084")["curva"] == original
    assert huellas(COPIA_TRABAJO)["sha256"] == antes


def test_la_curva_de_la_hoja_sigue_siendo_aceptable(hojas):
    hoja = next(h for h in hojas if h["pozo"] == "QF-084")
    curva = [{"caudal_bfpd": p["caudal_bfpd"], "head_ft": p["head_ft"]} for p in hoja["curva"]]
    caudales = [p["caudal_bfpd"] for p in curva]
    assert all(caudales[i + 1] > caudales[i] for i in range(len(caudales) - 1))
    resultado = evaluar_solicitud(_solicitud(curva), hojas=hojas)
    assert resultado["estado_evaluacion"] == "completada_preliminar"
    assert next(r["id"] for r in resultado["reglas"] if r.get("activada")) == "RC-BES-03"
    evidencia = next(r for r in resultado["reglas"] if r.get("activada"))["evidencia"]
    assert evidencia["limite_maximo_a_frecuencia_bfpd"] == pytest.approx(10500)
    assert resultado["recomendacion_operacional_autorizada"] is False


def test_interpolacion_analitica_en_el_vertice_y_entre_puntos():
    curva = [
        {"caudal_bfpd": 0, "head_ft": 100, "brake_hp": 999},
        {"caudal_bfpd": 100, "head_ft": 0, "eff_numero": 0.5},
    ]
    copia = [dict(p) for p in curva]

    def esperado(thd):
        return 0 + (thd - 100) / (0 - 100) * (100 - 0)

    en_vertice = caudal_a_producir(100, curva, 60, 60, 1)
    entre = caudal_a_producir(40, curva, 60, 60, 1)
    assert en_vertice.resultados["caudal_a_producir_bfpd"]["valor"] == pytest.approx(esperado(100))
    assert entre.resultados["caudal_a_producir_bfpd"]["valor"] == pytest.approx(esperado(40))
    assert esperado(40) == pytest.approx(60)
    assert caudal_a_producir(100.1, curva, 60, 60, 1).estado == "no_calculable"
    assert caudal_a_producir(0, curva, 60, 60, 1).estado == "no_calculable"
    assert curva == copia


def test_la_fecha_mala_y_el_retroceso_se_rechazan_juntos(hojas, monkeypatch):
    monkeypatch.setattr(
        "evaluacion.motor.calcular_hoja",
        lambda _hoja: (_ for _ in ()).throw(AssertionError("no calcular")),
    )
    solicitud = _solicitud([
        {"caudal_bfpd": 0, "head_ft": 100},
        {"caudal_bfpd": 200, "head_ft": 50},
        {"caudal_bfpd": 100, "head_ft": 0},
    ])
    solicitud["fecha_observacion"] = "ayer"
    resultado = evaluar_solicitud(solicitud, hojas=hojas)
    codigos = {e["codigo"] for e in resultado["errores"]}
    assert "FORMATO_INVALIDO" in codigos
    assert "ESTRUCTURA_INVALIDA" in codigos
    assert resultado["modelos"] == []
