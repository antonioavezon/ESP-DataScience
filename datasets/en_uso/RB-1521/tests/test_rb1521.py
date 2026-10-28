"""Integridad de la copia, partición y motor. No abre el original de fuentes/."""

from pathlib import Path

from evaluacion.motor import evaluar_solicitud
from rb1521_lectura import HASH_ORIGINAL, fecha_iso, huella, leer_serie
from rb1521_particion import contar_identidades, identidad_exacta, particionar

ENTRADA = Path(__file__).resolve().parents[1] / "entrada" / "RB-1521-PY-121120.xls"
ORIGINAL = Path(__file__).resolve().parents[4] / "fuentes" / "originales" / "RB-1521-PY-121120.xls"


def test_la_copia_conserva_el_hash_y_no_altera_el_original():
    assert huella(ENTRADA) == HASH_ORIGINAL
    assert huella(ORIGINAL) == HASH_ORIGINAL
    assert ENTRADA.read_bytes() == ORIGINAL.read_bytes()


def test_la_serie_tiene_129_dias_continuos_y_una_bomba():
    serie = leer_serie()
    assert len(serie) == 129
    assert fecha_iso(serie[0]["Fecha"]) == "2020-05-02"
    assert fecha_iso(serie[-1]["Fecha"]) == "2020-09-07"
    deltas = [(serie[i]["Fecha"] - serie[i - 1]["Fecha"]).days for i in range(1, len(serie))]
    assert deltas == [1] * 128
    assert {fila["Marca-Bomba"] for fila in serie} == {"S11000N"}


def test_la_particion_cierra_en_128_dias_y_falla_el_9_de_julio():
    serie = leer_serie()
    assert contar_identidades(serie) == 128
    excepciones = [fila for fila in serie if not identidad_exacta(fila)]
    assert [fecha_iso(fila["Fecha"]) for fila in excepciones] == ["2020-07-09"]
    agua, petroleo = particionar(8977.0, 0.985)
    assert agua == 8842.345
    assert abs(petroleo - 134.655) < 1e-9


def test_el_motor_reproduce_el_dia_de_referencia_sin_inventar_presion():
    salida = evaluar_solicitud({"dataset_id": "RB-1521", "pozo_id": "RB-1521", "variables": []})
    assert salida["estado_evaluacion"] == "completada_preliminar"
    assert salida["recomendacion_operacional_autorizada"] is False
    assert salida["coincidencia_dia_referencia"] is True
    valores = salida["modelos"][0]["valores"]
    assert valores["q_water"] == 8842.345
    assert valores["dias_serie"] == 129
    assert valores["dias_identidad_exacta"] == 128
    assert "pip_ft" not in valores


def test_un_caudal_nuevo_reparte_y_deja_de_coincidir_con_la_fila():
    salida = evaluar_solicitud({
        "dataset_id": "RB-1521",
        "pozo_id": "RB-1521",
        "variables": [{"nombre": "caudal_fluidos", "valor": 8500, "unidad": "BFPD"}],
    })
    valores = salida["modelos"][0]["valores"]
    assert valores["q_water"] == 8500 * 0.985
    assert salida["coincidencia_dia_referencia"] is False


def test_rechaza_otro_pozo_y_una_entrada_ajena():
    assert evaluar_solicitud({"pozo_id": "QF-084"})["estado_evaluacion"] == "entrada_invalida"
    salida = evaluar_solicitud({
        "pozo_id": "RB-1521",
        "variables": [{"nombre": "frecuencia_hz", "valor": 44, "unidad": "Hz"}],
    })
    assert salida["estado_evaluacion"] == "entrada_invalida"
