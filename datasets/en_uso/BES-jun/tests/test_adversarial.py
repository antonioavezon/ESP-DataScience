"""Entradas adversas. Un tipo incorrecto no es una excepción ni una respuesta fuera de esquema."""

import json
import random

import pytest

from evaluacion.contratos import VERSION_CONTRATO, errores_de_salida
from evaluacion.motor import evaluar, evaluar_json, evaluar_solicitud
from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO


def _base(**extra):
    solicitud = {
        "dataset_id": "BES-jun",
        "pozo_id": "QF-084",
        "version_configuracion": VERSION_CONTRATO,
        "variables": [],
    }
    solicitud.update(extra)
    return solicitud


@pytest.fixture(scope="module")
def hojas():
    from ingesta.leer_bes_jun import leer_libro
    return leer_libro()


@pytest.mark.parametrize("nombre", [None, True, 63, 1.5, ["frecuencia_hz"], {"a": 1}, [["x"]], {"n": {"m": 1}}])
def test_un_nombre_que_no_es_texto_no_lanza(hojas, nombre):
    solicitud = _base(variables=[{"nombre": nombre, "valor": 63, "unidad": "Hz", "procedencia": "operador"}])
    resultado = evaluar_solicitud(solicitud, hojas=hojas)
    assert resultado["estado_evaluacion"] == "entrada_invalida"
    assert resultado["reglas_ejecutadas"] == 0
    assert resultado["recomendacion_operacional_autorizada"] is False
    assert errores_de_salida(resultado) == []
    assert any(e["codigo"] == "TIPO_INVALIDO" for e in resultado["errores"])


@pytest.mark.parametrize("campo,valor", [
    ("fecha_observacion", 23),
    ("fecha_observacion", ["2026-10-20"]),
    ("escenario_id", 1234),
    ("dataset_id", {"id": "BES-jun"}),
    ("pozo_id", ["QF-084"]),
    ("version_configuracion", 1.3),
    ("modo", {"tipo": "operacional"}),
])
def test_un_campo_mal_tipado_no_se_copia_a_la_respuesta(hojas, campo, valor):
    resultado = evaluar_solicitud(_base(**{campo: valor}), hojas=hojas)
    assert resultado["estado_evaluacion"] == "entrada_invalida"
    assert resultado["fecha_referencia"] is None or isinstance(resultado["fecha_referencia"], str)
    assert resultado["escenario_id"] is None or isinstance(resultado["escenario_id"], str)
    assert isinstance(resultado["dataset_solicitado"], str)
    assert isinstance(resultado["pozo_solicitado"], str)
    assert errores_de_salida(resultado) == []
    assert resultado["recomendacion_operacional_autorizada"] is False


@pytest.mark.parametrize("texto", ["", "null", "[]", '"BES-jun"', "{", "{}"])
def test_json_de_raiz_incorrecta_es_controlado(texto):
    resultado = evaluar_json(texto)
    assert resultado["estado_evaluacion"] == "entrada_invalida"
    assert errores_de_salida(resultado) == []
    assert resultado["reglas_ejecutadas"] == 0


def test_json_demasiado_grande_no_se_interpreta():
    from evaluacion.contratos import MAX_CARACTERES_JSON
    resultado = evaluar_json("{" + (" " * (MAX_CARACTERES_JSON + 1)) + "}")
    assert any(e["codigo"] == "LIMITE_TAMANO" for e in resultado["errores"])
    assert errores_de_salida(resultado) == []


def test_lista_de_variables_excesiva_no_se_recorre(hojas):
    variables = [
        {"nombre": "frecuencia_hz", "valor": 60, "unidad": "Hz", "procedencia": "operador"}
        for _ in range(80)
    ]
    resultado = evaluar_solicitud(_base(variables=variables), hojas=hojas)
    assert any(e["codigo"] == "LIMITE_TAMANO" for e in resultado["errores"])
    assert resultado["modelos"] == []
    assert errores_de_salida(resultado) == []


def test_la_misma_solicitud_dos_veces_da_el_mismo_estado(hojas):
    solicitud = _base()
    primera = evaluar_solicitud(solicitud, hojas=hojas)
    segunda = evaluar_solicitud(json.loads(json.dumps(solicitud)), hojas=hojas)
    assert primera["estado_evaluacion"] == segunda["estado_evaluacion"]
    assert [r["id"] for r in primera["reglas"] if r.get("activada")] == [r["id"] for r in segunda["reglas"] if r.get("activada")]


def test_el_orden_de_variables_distintas_no_cambia_la_regla(hojas):
    a = {"nombre": "caudal_operacion_bfpd", "valor": 10301, "unidad": "BFPD", "procedencia": "operador"}
    b = {"nombre": "frecuencia_hz", "valor": 63, "unidad": "Hz", "procedencia": "sensor"}
    uno = evaluar_solicitud(_base(variables=[a, b]), hojas=hojas)
    otro = evaluar_solicitud(_base(variables=[b, a]), hojas=hojas)
    assert next(r["id"] for r in uno["reglas"] if r.get("activada")) == next(r["id"] for r in otro["reglas"] if r.get("activada"))


def test_tipos_generados_con_semilla_no_rompen_el_esquema(hojas):
    azar = random.Random(20261020)
    muestras = [None, True, False, 0, 1, -1, 1.5, "alto", "", [], {}, ["frecuencia_hz"], {"nombre": "x"}]
    for _ in range(40):
        solicitud = _base(variables=[{
            "nombre": azar.choice(muestras),
            "valor": azar.choice(muestras),
            "unidad": azar.choice(muestras),
            "procedencia": azar.choice(muestras),
        }])
        resultado = evaluar_solicitud(solicitud, hojas=hojas)
        assert resultado["estado_evaluacion"] == "entrada_invalida"
        assert resultado["reglas_ejecutadas"] == 0
        assert errores_de_salida(resultado) == [], solicitud


def test_una_excepcion_de_modelo_no_expone_la_traza_y_queda_registrada(hojas, monkeypatch):
    from ingesta.leer_bes_jun import raiz_expediente

    def _falla(_hoja):
        raise RuntimeError("fallo de prueba en /home/antonio/no-mostrar")

    monkeypatch.setattr("evaluacion.motor.calcular_hoja", _falla)
    antes = huellas(COPIA_TRABAJO)["sha256"]
    resultado = evaluar("BES-jun", "QF-084", hojas=hojas)
    assert resultado["estado_evaluacion"] == "error_interno"
    assert resultado["incidente_id"].startswith("INC-")
    assert resultado["reglas_ejecutadas"] == 0
    assert resultado["modelos"] == []
    assert resultado["recomendacion_operacional_autorizada"] is False
    texto = json.dumps(resultado)
    assert "/home/antonio" not in texto
    assert "Traceback" not in texto
    assert errores_de_salida(resultado) == []
    registro = (raiz_expediente() / "logs" / "incidentes.jsonl").read_text(encoding="utf-8")
    assert resultado["incidente_id"] in registro
    assert "RuntimeError" in registro
    assert huellas(COPIA_TRABAJO)["sha256"] == antes


def test_la_evaluacion_no_cambia_el_excel_ni_la_ficha(hojas):
    antes = huellas(COPIA_TRABAJO)["sha256"]
    limite = next(h["limite_maximo_bfpd"] for h in hojas if h["pozo"] == "QF-084")
    evaluar_solicitud(_base(variables=[
        {"nombre": "limite_maximo_bfpd", "valor": 20000, "unidad": "BFPD", "procedencia": "operador"},
    ]), hojas=hojas)
    assert huellas(COPIA_TRABAJO)["sha256"] == antes
    assert next(h["limite_maximo_bfpd"] for h in hojas if h["pozo"] == "QF-084") == limite


def test_las_plantillas_publicadas_se_vuelven_a_ejecutar(hojas):
    from ingesta.leer_bes_jun import raiz_expediente
    carpeta = raiz_expediente() / "integracion" / "ejemplos" / "plantillas"
    archivos = sorted(carpeta.glob("*.json"))
    assert len(archivos) == 10
    for ruta in archivos:
        documento = json.loads(ruta.read_text(encoding="utf-8"))
        fresco = evaluar_solicitud(documento["solicitud"], hojas=hojas)
        assert fresco["estado_evaluacion"] == documento["resultado"]["estado_evaluacion"]
        assert fresco["recomendacion_operacional_autorizada"] is False
        assert errores_de_salida(fresco) == []
        assert "promedio" not in json.dumps(fresco, ensure_ascii=False).casefold()


def _simulacion(**escenario):
    return _base(modo="simulacion", escenario_id="prueba-01", parametros_escenario=escenario)


def test_una_curva_de_un_numero_no_llega_al_calculo(hojas, monkeypatch):
    def _prohibido(_hoja):
        raise AssertionError("el modelo no debe ejecutarse")

    monkeypatch.setattr("evaluacion.motor.calcular_hoja", _prohibido)
    resultado = evaluar_solicitud(_simulacion(curva=[123]), hojas=hojas)
    assert resultado["estado_evaluacion"] == "entrada_invalida"
    assert resultado["modelos"] == []
    assert resultado["reglas_ejecutadas"] == 0
    assert resultado["recomendacion_operacional_autorizada"] is False
    assert errores_de_salida(resultado) == []
    errores = resultado["errores"]
    assert any("curva" in e["campo"] for e in errores)
    texto = json.dumps(resultado, ensure_ascii=False)
    assert "Traceback" not in texto
    assert "promedio" not in texto.casefold()
    assert next(h for h in hojas if h["pozo"] == "QF-084")["curva"][0]["caudal_bfpd"] != 123


@pytest.mark.parametrize("curva,codigo", [
    ([], "ESTRUCTURA_INVALIDA"),
    (["alto", "bajo"], "TIPO_INVALIDO"),
    ([{"caudal_bfpd": 0, "head_ft": 10}], "ESTRUCTURA_INVALIDA"),
    ([{"caudal_bfpd": 0}, {"caudal_bfpd": 10, "head_ft": 0}], "CAMPO_OBLIGATORIO"),
    ([{"caudal_bfpd": 0, "head_ft": 10, "eff_numero": 0.5}, {"caudal_bfpd": 10, "head_ft": 0}], "CAMPO_DESCONOCIDO"),
    ([{"caudal_bfpd": 0, "head_ft": 10}, {"caudal_bfpd": 0, "head_ft": 0}], "ESTRUCTURA_INVALIDA"),
    ([{"caudal_bfpd": 10, "head_ft": 0}, {"caudal_bfpd": 0, "head_ft": 10}], "ESTRUCTURA_INVALIDA"),
    ([{"caudal_bfpd": float("nan"), "head_ft": 10}, {"caudal_bfpd": 10, "head_ft": 0}], "VALOR_NO_FINITO"),
])
def test_curvas_mal_formadas_son_entrada_invalida(hojas, monkeypatch, curva, codigo):
    monkeypatch.setattr("evaluacion.motor.calcular_hoja", lambda _hoja: (_ for _ in ()).throw(AssertionError("no calcular")))
    resultado = evaluar_solicitud(_simulacion(curva=curva), hojas=hojas)
    assert resultado["estado_evaluacion"] == "entrada_invalida"
    assert resultado["modelos"] == []
    assert any(e["codigo"] == codigo and "curva" in e["campo"] for e in resultado["errores"])
    assert errores_de_salida(resultado) == []
    assert "Traceback" not in json.dumps(resultado)


def test_un_parametro_con_campo_inesperado_se_rechaza(hojas, monkeypatch):
    monkeypatch.setattr("evaluacion.motor.calcular_hoja", lambda _hoja: (_ for _ in ()).throw(AssertionError("no calcular")))
    resultado = evaluar_solicitud(_simulacion(etapas={"valor": 53, "unidad": "1", "campo_inesperado": "dato"}), hojas=hojas)
    assert resultado["estado_evaluacion"] == "entrada_invalida"
    assert resultado["modelos"] == []
    assert any(e["codigo"] == "CAMPO_DESCONOCIDO" and "etapas" in e["campo"] for e in resultado["errores"])
    assert errores_de_salida(resultado) == []


def test_unidad_de_escenario_incorrecta_o_ausente(hojas, monkeypatch):
    monkeypatch.setattr("evaluacion.motor.calcular_hoja", lambda _hoja: (_ for _ in ()).throw(AssertionError("no calcular")))
    sin_unidad = evaluar_solicitud(_simulacion(etapas={"valor": 53}), hojas=hojas)
    otra = evaluar_solicitud(_simulacion(etapas={"valor": 53, "unidad": "ft"}), hojas=hojas)
    assert any(e["codigo"] in ("UNIDAD_AUSENTE", "CAMPO_OBLIGATORIO") and "etapas" in e["campo"] for e in sin_unidad["errores"])
    assert any(e["codigo"] == "UNIDAD_INCOMPATIBLE" and e.get("unidad_esperada") == "1" for e in otra["errores"])
    assert sin_unidad["modelos"] == [] and otra["modelos"] == []


@pytest.mark.parametrize("campo,valor,codigo", [
    ("pozo_id", "   ", "IDENTIFICADOR_MAL_FORMADO"),
    ("pozo_id", " QF-084 ", "IDENTIFICADOR_MAL_FORMADO"),
    ("escenario_id", "  ", "IDENTIFICADOR_MAL_FORMADO"),
    ("fecha_observacion", "23/10/2026", "FORMATO_INVALIDO"),
    ("fecha_observacion", "2026-13-40", "FORMATO_INVALIDO"),
])
def test_identificadores_y_fechas_mal_formados(hojas, campo, valor, codigo):
    extra = {campo: valor}
    if campo == "escenario_id":
        extra["modo"] = "simulacion"
    resultado = evaluar_solicitud(_base(**extra), hojas=hojas)
    assert resultado["estado_evaluacion"] == "entrada_invalida"
    assert any(e["codigo"] == codigo and e["campo"] == campo for e in resultado["errores"])
    assert resultado["modelos"] == []
    assert "Traceback" not in json.dumps(resultado)
    assert errores_de_salida(resultado) == []


def test_una_fecha_iso_no_cambia_el_significado_de_la_medicion(hojas):
    resultado = evaluar_solicitud(_base(fecha_observacion="2026-10-20T15:00:00-03:00"), hojas=hojas)
    assert resultado["estado_evaluacion"] == "completada_preliminar"
    assert resultado["fecha_referencia"] == "2026-10-20T15:00:00-03:00"
    assert resultado["recomendacion_operacional_autorizada"] is False


def test_una_curva_bien_formada_no_reescribe_la_ficha(hojas):
    original = [dict(p) for p in next(h for h in hojas if h["pozo"] == "QF-084")["curva"]]
    curva = [
        {"caudal_bfpd": 0, "head_ft": 400},
        {"caudal_bfpd": 20000, "head_ft": 0},
    ]
    resultado = evaluar_solicitud(_simulacion(curva=curva, etapas={"valor": 1, "unidad": "1"}), hojas=hojas)
    assert resultado["estado_evaluacion"] in ("completada_preliminar", "no_evaluable")
    assert resultado["hipotetico"] is True
    assert "curva" in resultado["parametros_modificados"]
    assert resultado["recomendacion_operacional_autorizada"] is False
    assert errores_de_salida(resultado) == []
    assert next(h for h in hojas if h["pozo"] == "QF-084")["curva"] == original


def test_los_mensajes_no_proponen_un_promedio(hojas):
    resultado = evaluar_solicitud(_base(variables=[
        {"nombre": "frecuencia_hz", "valor": "alto", "unidad": "Hz", "procedencia": "operador"},
    ]), hojas=hojas)
    texto = json.dumps(resultado, ensure_ascii=False).casefold()
    assert "promedio" not in texto
    assert any(e["codigo"] == "TIPO_INVALIDO" and e.get("tipo_esperado") for e in resultado["errores"])
    assert errores_de_salida(resultado) == []
