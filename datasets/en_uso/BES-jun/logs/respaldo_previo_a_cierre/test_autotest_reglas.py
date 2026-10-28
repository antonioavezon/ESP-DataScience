"""AutoTest de reglas, entradas inválidas, trazabilidad y contratos.

Los cinco pozos y la clasificación esperada están escritos aquí.
No se obtienen llamando a ``comparar_caudal_con_limites``.
"""

import json
import math
from copy import deepcopy

import pytest
from jsonschema import Draft202012Validator

from analisis.catalogo_bes_jun import FORMULAS
from catalogo.variables_bes_jun import VARIABLES
from evaluacion.contratos import VERSION_CONTRATO, errores_de_salida, esquema_entrada, esquema_salida
from evaluacion.motor import evaluar, evaluar_solicitud
from ingesta.leer_bes_jun import raiz_expediente
from reglas.catalogo import REGLAS, markdown_reglas, por_id
from reglas.trazabilidad import CORRESPONDENCIA

# Especificación independiente. qmax(f) = qmax_60 * f / 60, con f_base = 60.
POZOS = (
    {"hoja": "QF-554H", "pozo": "QF-084", "hz": 63, "caudal": 10301, "qmin60": 2500, "qmax60": 10000},
    {"hoja": "QF-545H", "pozo": "QF-301", "hz": 57, "caudal": 8767, "qmin60": 2500, "qmax60": 10000},
    {"hoja": "QF-500H", "pozo": "QF-147", "hz": 56, "caudal": 7728, "qmin60": 2500, "qmax60": 10000},
    {"hoja": "QF-378HST", "pozo": "QF-005", "hz": 67, "caudal": 7116, "qmin60": 2000, "qmax60": 8000},
    {"hoja": "QF-549HST", "pozo": "QF-306", "hz": 62, "caudal": 5419, "qmin60": 2000, "qmax60": 8000},
)
FRASES_PROHIBIDAS = ("disminuya la frecuencia", "baje la frecuencia", "suba la frecuencia", "operación segura", "pozo está seguro", "pozo esta seguro")


@pytest.fixture(scope="module")
def hojas():
    from ingesta.leer_bes_jun import leer_libro
    return leer_libro()


def _activada(resultado):
    return next(r for r in resultado["reglas"] if r.get("activada"))


def _con(caudal=None, frecuencia=None, extra=None):
    entradas = {}
    unidades = {}
    if caudal is not None:
        entradas["caudal_operacion_bfpd"] = caudal
        unidades["caudal_operacion_bfpd"] = "BFPD"
    if frecuencia is not None:
        entradas["frecuencia_hz"] = frecuencia
        unidades["frecuencia_hz"] = "Hz"
    if extra:
        entradas.update(extra["valores"])
        unidades.update(extra["unidades"])
    entradas["unidades"] = unidades
    return entradas


def test_la_hoja_coincide_con_la_especificacion_y_los_cinco_son_rc_bes_03(hojas):
    for caso in POZOS:
        hoja = next(h for h in hojas if h["pozo"] == caso["pozo"])
        assert hoja["hoja"] == caso["hoja"]
        assert hoja["frecuencia_hz"] == caso["hz"]
        assert hoja["caudal_operacion_bfpd"] == caso["caudal"]
        assert hoja["limite_minimo_bfpd"] == caso["qmin60"]
        assert hoja["limite_maximo_bfpd"] == caso["qmax60"]
        qmin = caso["qmin60"] * caso["hz"] / 60
        qmax = caso["qmax60"] * caso["hz"] / 60
        assert qmin <= caso["caudal"] <= qmax
        resultado = evaluar("BES-jun", caso["pozo"], hojas=hojas)
        regla = _activada(resultado)
        assert regla["id"] == "RC-BES-03"
        assert regla["estado_regla"] == "pendiente_validacion"
        assert math.isclose(regla["evidencia"]["limite_maximo_a_frecuencia_bfpd"], qmax)
        assert resultado["recomendacion_operacional_autorizada"] is False
        assert resultado["reglas_ejecutadas"] == 3
        texto = json.dumps(resultado, ensure_ascii=False).casefold()
        assert not any(frase in texto for frase in FRASES_PROHIBIDAS)
        assert errores_de_salida(resultado) == []


def test_qf084_no_vuelve_a_rc_bes_01(hojas):
    caso = POZOS[0]
    assert caso["qmax60"] * caso["hz"] / 60 == 10500
    resultado = evaluar("BES-jun", "QF-084", hojas=hojas)
    assert _activada(resultado)["id"] == "RC-BES-03"
    assert _activada(resultado)["evidencia"]["comparacion_sin_escalar"]["id"] == "RC-BES-01"


def test_rc_bes_01_solo_por_encima_del_maximo_escalado(hojas):
    qmax = 10500
    dentro = evaluar("BES-jun", "QF-084", _con(caudal=qmax - 1), hojas=hojas)
    igual = evaluar("BES-jun", "QF-084", _con(caudal=qmax), hojas=hojas)
    fuera = evaluar("BES-jun", "QF-084", _con(caudal=qmax + 0.01), hojas=hojas)
    assert _activada(dentro)["id"] == "RC-BES-03"
    assert _activada(igual)["id"] == "RC-BES-03"
    assert _activada(fuera)["id"] == "RC-BES-01"
    assert _activada(fuera)["aprobada_para_uso_operacional"] is False


def test_rc_bes_02_solo_por_debajo_del_minimo_escalado(hojas):
    qmin = 2500 * 63 / 60
    debajo = evaluar("BES-jun", "QF-084", _con(caudal=qmin - 1), hojas=hojas)
    igual = evaluar("BES-jun", "QF-084", _con(caudal=qmin), hojas=hojas)
    encima = evaluar("BES-jun", "QF-084", _con(caudal=qmin + 1), hojas=hojas)
    assert _activada(debajo)["id"] == "RC-BES-02"
    assert _activada(igual)["id"] == "RC-BES-03"
    assert _activada(encima)["id"] == "RC-BES-03"
    ids = {r["id"] for r in debajo["reglas"] if r.get("activada")}
    assert ids == {"RC-BES-02"}


def test_limites_contradictorios_no_clasifican(hojas):
    extra = {"valores": {"limite_minimo_bfpd": 9000, "limite_maximo_bfpd": 1000},
             "unidades": {"limite_minimo_bfpd": "BFPD", "limite_maximo_bfpd": "BFPD"}}
    resultado = evaluar("BES-jun", "QF-084", _con(extra=extra), hojas=hojas)
    assert resultado["estado_evaluacion"] == "no_evaluable"
    assert resultado["reglas_ejecutadas"] == 0
    assert not any(r.get("activada") for r in resultado["reglas"])


def test_sin_limite_minimo_no_es_evaluable(hojas):
    copia = deepcopy(hojas)
    next(h for h in copia if h["pozo"] == "QF-084")["limite_minimo_bfpd"] = None
    resultado = evaluar("BES-jun", "QF-084", hojas=copia)
    assert resultado["estado_evaluacion"] == "no_evaluable"
    assert resultado["recomendacion_operacional_autorizada"] is False


def test_rc_bes_04_sigue_no_evaluable_y_cita_ct_06(hojas):
    resultado = evaluar("BES-jun", "QF-084", hojas=hojas)
    regla = next(r for r in resultado["reglas"] if r["id"] == "RC-BES-04")
    assert regla["evaluable"] is False and regla["estado_regla"] == "no_evaluable"
    assert regla["consultas_tecnicas"] == ["CT-06"]
    assert "CT-09" not in regla["consultas_tecnicas"]
    assert por_id("RC-BES-04")["estado_validacion"] == "no_evaluable"


@pytest.mark.parametrize("entradas,codigo", [
    ({"frecuencia_hz": "alto", "unidades": {"frecuencia_hz": "Hz"}}, "TIPO_INVALIDO"),
    ({"caudal_operacion_bfpd": "mucho", "unidades": {"caudal_operacion_bfpd": "BFPD"}}, "TIPO_INVALIDO"),
    ({"frecuencia_hz": float("inf"), "unidades": {"frecuencia_hz": "Hz"}}, "VALOR_NO_FINITO"),
    ({"caudal_operacion_bfpd": float("nan"), "unidades": {"caudal_operacion_bfpd": "BFPD"}}, "VALOR_NO_FINITO"),
    ({"frecuencia_hz": 0, "unidades": {"frecuencia_hz": "Hz"}}, "FISICAMENTE_INADMISIBLE"),
    ({"frecuencia_hz": -5, "unidades": {"frecuencia_hz": "Hz"}}, "FISICAMENTE_INADMISIBLE"),
    ({"caudal_operacion_bfpd": -1, "unidades": {"caudal_operacion_bfpd": "BFPD"}}, "FISICAMENTE_INADMISIBLE"),
    ({"frecuencia_hz": True, "unidades": {"frecuencia_hz": "Hz"}}, "TIPO_INVALIDO"),
    ({"caudal_operacion_bfpd": 1000}, "UNIDAD_AUSENTE"),
    ({"campo_inventado": 1, "unidades": {"campo_inventado": "BFPD"}}, "CAMPO_DESCONOCIDO"),
])
def test_entradas_invalidas_no_lanzan_y_no_ejecutan_reglas(hojas, entradas, codigo):
    resultado = evaluar("BES-jun", "QF-084", entradas, hojas=hojas)
    assert resultado["estado_evaluacion"] == "entrada_invalida"
    assert resultado["reglas_ejecutadas"] == 0
    assert resultado["modelos"] == []
    assert any(e["codigo"] == codigo for e in resultado["errores"])
    json.dumps(resultado)


def test_solicitud_sin_version_o_con_version_vieja_o_dataset_ajeno(hojas):
    base = {"dataset_id": "BES-jun", "pozo_id": "QF-084", "variables": []}
    sin_version = evaluar_solicitud(base, hojas=hojas)
    assert any(e["codigo"] == "VERSION_AUSENTE" for e in sin_version["errores"])
    vieja = evaluar_solicitud({**base, "version_configuracion": "1.0.0"}, hojas=hojas)
    assert any(e["codigo"] == "VERSION_INCOMPATIBLE" for e in vieja["errores"])
    ajena = evaluar_solicitud({**base, "version_configuracion": VERSION_CONTRATO, "dataset_id": "RB-1521"}, hojas=hojas)
    assert any(e["codigo"] == "DATASET_DESCONOCIDO" for e in ajena["errores"])
    for resultado in (sin_version, vieja, ajena):
        assert resultado["estado_evaluacion"] == "entrada_invalida"
        assert resultado["reglas_ejecutadas"] == 0


def test_solicitud_con_texto_campo_desconocido_y_estructura_mala(hojas):
    texto = evaluar_solicitud({
        "dataset_id": "BES-jun", "pozo_id": "QF-084", "version_configuracion": VERSION_CONTRATO,
        "variables": [{"nombre": "frecuencia_hz", "valor": "alto", "unidad": "Hz", "procedencia": "operador"}],
    }, hojas=hojas)
    assert any(e["codigo"] == "TIPO_INVALIDO" for e in texto["errores"])
    desconocido = evaluar_solicitud({
        "dataset_id": "BES-jun", "pozo_id": "QF-084", "version_configuracion": VERSION_CONTRATO, "sorpresa": 1,
    }, hojas=hojas)
    assert any(e["codigo"] == "CAMPO_DESCONOCIDO" for e in desconocido["errores"])
    mala = evaluar_solicitud(["no", "es", "un", "objeto"], hojas=hojas)
    assert mala["estado_evaluacion"] == "entrada_invalida"
    assert any(e["codigo"] == "ESTRUCTURA_INVALIDA" for e in mala["errores"])


def test_pozo_desconocido_es_controlado(hojas):
    resultado = evaluar_solicitud({
        "dataset_id": "BES-jun", "pozo_id": "NO-EXISTE", "version_configuracion": VERSION_CONTRATO,
    }, hojas=hojas)
    assert resultado["estado_evaluacion"] == "no_evaluable"
    assert resultado["reglas_ejecutadas"] == 0


def test_la_salida_valida_cumple_el_esquema_y_la_invalida_tambien_se_serializa(hojas):
    solicitud = {"dataset_id": "BES-jun", "pozo_id": "QF-084", "version_configuracion": VERSION_CONTRATO, "fecha_observacion": None, "variables": []}
    Draft202012Validator(esquema_entrada()).validate(solicitud)
    salida = evaluar_solicitud(solicitud, hojas=hojas)
    Draft202012Validator(esquema_salida()).validate(salida)
    assert json.loads(json.dumps(salida))["reglas"][0]["version"]


def test_trazabilidad_de_reglas_coincide_con_la_matriz_revisada():
    consultas = (raiz_expediente() / "docs" / "consultas_tecnicas_pendientes.md").read_text(encoding="utf-8")
    nombres = {v["nombre"] for v in VARIABLES}
    ecuaciones = {f["id"] for f in FORMULAS}
    assert set(CORRESPONDENCIA) == {r["id"] for r in REGLAS}
    for regla in REGLAS:
        esperado = CORRESPONDENCIA[regla["id"]]
        assert tuple(regla["consultas_tecnicas"]) == esperado["consultas"]
        for consulta in esperado["consultas"]:
            assert f"| {consulta} |" in consultas
        for variable in esperado["variables"]:
            assert variable in nombres
            assert variable in regla["variables_requeridas"]
        for ecuacion in esperado["ecuaciones"]:
            assert ecuacion in ecuaciones
            assert ecuacion in regla["ecuaciones_dependientes"]
        assert esperado["porque"]
    assert "CT-09" not in CORRESPONDENCIA["RC-BES-04"]["consultas"]
    texto = markdown_reglas()
    bloque = texto.split("## RC-BES-04")[1].split("## ")[0]
    assert "CT-06" in bloque and "CT-09" not in bloque


def test_los_documentos_vigentes_no_clasifican_qf084_como_rc_bes_01():
    raiz = raiz_expediente()
    informe = (raiz / "reports" / "informe_analisis_BES-jun.md").read_text(encoding="utf-8")
    ficha = (raiz / "docs" / "ficha_maestra_BES-jun.md").read_text(encoding="utf-8")
    discrepancias = (raiz / "docs" / "discrepancias_cientificas.md").read_text(encoding="utf-8")
    assert "RC-BES-01 se activa solo en QF-084" not in informe
    assert "clasificación preliminar es RC-BES-03" in ficha or "RC-BES-03" in ficha
    assert "CT-06" in discrepancias.split("Columna EFF")[1].split("\n")[0]
