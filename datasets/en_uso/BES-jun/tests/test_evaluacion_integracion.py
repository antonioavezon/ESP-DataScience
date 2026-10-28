"""Motor, contratos y la clasificación vigente de QF-084."""

import json
import math

import pytest

from evaluacion.contratos import errores_de_salida
from evaluacion.motor import evaluar, evaluar_solicitud
from informes.escribir_informe import _markdown
from ingesta.leer_bes_jun import leer_libro
from ingesta.survey import leer_survey
from reglas.catalogo import REGLAS, disposicion


@pytest.fixture(scope="module")
def hojas():
    return leer_libro()


def _activada(resultado: dict) -> dict:
    return next(r for r in resultado["reglas"] if r.get("activada"))


def test_qf084_con_datos_registrados_es_rc_bes_03_y_no_autoriza_operar(hojas):
    resultado = evaluar("BES-jun", "QF-084", hojas=hojas)
    assert resultado["estado_evaluacion"] == "completada_preliminar"
    assert resultado["recomendacion_operacional_autorizada"] is False
    regla = _activada(resultado)
    assert regla["id"] == "RC-BES-03"
    assert regla["aprobada_para_uso_operacional"] is False
    assert regla["estado_regla"] == "pendiente_validacion"
    evidencia = regla["evidencia"]
    assert math.isclose(evidencia["caudal_operacion_bfpd"], 10301)
    assert math.isclose(evidencia["frecuencia_operacion_hz"], 63)
    assert math.isclose(evidencia["limite_maximo_escrito_a_60_hz_bfpd"], 10000)
    assert math.isclose(evidencia["limite_maximo_a_frecuencia_bfpd"], 10500)
    assert evidencia["comparacion_sin_escalar"]["id"] == "RC-BES-01"
    assert "Disminuya" not in json.dumps(resultado, ensure_ascii=False)
    assert errores_de_salida(resultado) == []


def test_la_hoja_qf554h_resuelve_el_mismo_pozo(hojas):
    assert _activada(evaluar("BES-jun", "QF-554H", hojas=hojas))["id"] == "RC-BES-03"


def test_igualdad_en_el_maximo_escalado_sigue_dentro(hojas):
    resultado = evaluar(
        "BES-jun", "QF-084",
        {"caudal_operacion_bfpd": 10500, "unidades": {"caudal_operacion_bfpd": "BFPD"}},
        hojas=hojas,
    )
    assert _activada(resultado)["id"] == "RC-BES-03"
    assert resultado["recomendacion_operacional_autorizada"] is False


def test_por_encima_del_maximo_escalado_avisa_sin_ordenar(hojas):
    resultado = evaluar(
        "BES-jun", "QF-084",
        {"caudal_operacion_bfpd": 10500.01, "unidades": {"caudal_operacion_bfpd": "BFPD"}},
        hojas=hojas,
    )
    regla = _activada(resultado)
    assert regla["id"] == "RC-BES-01"
    assert regla["tipo_mensaje"] == "advertencia"
    assert regla["aprobada_para_uso_operacional"] is False
    assert resultado["recomendacion_operacional_autorizada"] is False


def test_sin_caudal_no_elige_regla(hojas):
    resultado = evaluar(
        "BES-jun", "QF-084",
        {"caudal_operacion_bfpd": None, "unidades": {"caudal_operacion_bfpd": "BFPD"}},
        hojas=hojas,
    )
    assert resultado["estado_evaluacion"] == "entrada_invalida"
    assert resultado["reglas_ejecutadas"] == 0
    assert any(e["codigo"] == "VALOR_NULO" for e in resultado["errores"])
    assert resultado["recomendacion_operacional_autorizada"] is False


def test_unidad_equivocada_es_error(hojas):
    resultado = evaluar(
        "BES-jun", "QF-084",
        {"caudal_operacion_bfpd": 100, "unidades": {"caudal_operacion_bfpd": "m3/d"}},
        hojas=hojas,
    )
    assert resultado["estado_evaluacion"] == "entrada_invalida"
    assert any(e["codigo"] == "UNIDAD_INCOMPATIBLE" for e in resultado["errores"])
    assert resultado["reglas_ejecutadas"] == 0
    assert resultado["recomendacion_operacional_autorizada"] is False


def test_dataset_y_pozo_desconocidos(hojas):
    ajeno = evaluar("otro", "QF-084", hojas=hojas)
    assert ajeno["estado_evaluacion"] == "entrada_invalida"
    assert ajeno["reglas_ejecutadas"] == 0
    assert evaluar("BES-jun", "POZO-QUE-NO-ESTA", hojas=hojas)["estado_evaluacion"] == "no_evaluable"


def test_version_de_contrato_distinta(hojas):
    resultado = evaluar_solicitud(
        {"dataset_id": "BES-jun", "pozo_id": "QF-084", "version_configuracion": "0.0.1"},
        hojas=hojas,
    )
    assert resultado["estado_evaluacion"] == "entrada_invalida"
    assert any(e["codigo"] == "VERSION_INCOMPATIBLE" for e in resultado["errores"])


def test_frecuencia_fuera_del_observado_advierte_y_no_autoriza(hojas):
    resultado = evaluar(
        "BES-jun", "QF-084",
        {"frecuencia_hz": 80, "unidades": {"frecuencia_hz": "Hz"}},
        hojas=hojas,
    )
    assert resultado["fuera_de_dominio_observado"] is True
    assert resultado["recomendacion_operacional_autorizada"] is False


def test_rc04_no_es_evaluable(hojas):
    resultado = evaluar("BES-jun", "QF-084", hojas=hojas)
    rc04 = next(r for r in resultado["reglas"] if r["id"] == "RC-BES-04")
    assert rc04["evaluable"] is False and rc04["estado_regla"] == "no_evaluable"


def test_ninguna_regla_del_catalogo_esta_aprobada():
    assert all(disposicion(r) in ("preliminar", "no_evaluable") for r in REGLAS)
    suspendida = {"estado_validacion": "suspendida", "condicion": {"operador": "mayor_que"}, "aprobada_para_uso_operacional": False}
    assert disposicion(suspendida) == "no_ejecutar"


def test_el_informe_no_recupera_la_clasificacion_vieja_de_qf084(hojas):
    texto = _markdown(hojas, leer_survey())
    assert "RC-BES-01 se activa solo en QF-084" not in texto
    assert "queda por encima del máximo escrito" not in texto
    assert "RC-BES-03" in texto
    assert "10500" in texto or "10.500" in texto or "10,500" in texto


def test_promover_no_mueve_el_expediente():
    from ciclo.promocion import promover
    from ingesta.leer_bes_jun import raiz_expediente
    antes = raiz_expediente()
    informe = promover()
    assert informe["movido"] is False
    assert raiz_expediente() == antes
    assert informe["puede_moverse_a_procesadas"] is False


def test_una_salida_con_recomendacion_no_autorizada_no_pasa_el_contrato():
    falso = {
        "dataset_id": "BES-jun", "pozo_id": "QF-084", "version_contrato": "1.0.0", "version_motor": "0.1.0",
        "estado_evaluacion": "completada_preliminar", "identidad": {}, "modelos": [],
        "reglas": [{"id": "RC-BES-03", "estado_regla": "pendiente_validacion", "evaluable": True,
                    "aprobada_para_uso_operacional": False, "tipo_mensaje": "recomendacion_tecnica_validada"}],
        "advertencias": [], "mensajes": [], "recomendacion_operacional_autorizada": True,
    }
    assert errores_de_salida(falso)
