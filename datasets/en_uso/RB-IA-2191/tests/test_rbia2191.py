"""Integridad de la copia, identidad BOPD y motor. No abre el original para modificarlo."""

from pathlib import Path

from evaluacion.motor import evaluar_solicitud
from rbia2191_lectura import HASH_ORIGINAL, fecha_iso, formulas_bopd, huella, leer_serie
from rbia2191_particion import bsw_reproduce_bwpd, contar_identidades, identidad_exacta, particionar

ENTRADA = Path(__file__).resolve().parents[1] / "entrada" / "RB-IA-2191-Data.xlsx"
ORIGINAL = Path(__file__).resolve().parents[4] / "fuentes" / "originales" / "RB-IA-2191-Data.xlsx"


def test_la_copia_conserva_el_hash_y_no_altera_el_original():
    assert huella(ENTRADA) == HASH_ORIGINAL
    assert huella(ORIGINAL) == HASH_ORIGINAL
    assert ENTRADA.read_bytes() == ORIGINAL.read_bytes()


def test_la_serie_tiene_28_dias_continuos_y_un_solo_pozo_implicito():
    serie = leer_serie()
    assert len(serie) == 28
    assert fecha_iso(serie[0]["FECHA"]) == "2020-05-02"
    assert fecha_iso(serie[-1]["FECHA"]) == "2020-05-29"
    deltas = [(serie[i]["FECHA"] - serie[i - 1]["FECHA"]).days for i in range(1, len(serie))]
    assert deltas == [1] * 27
    assert {fila["BFPD"] for fila in serie} == {5180}
    assert {fila["BWPD"] for fila in serie} == {5099.4}


def test_bopd_cierra_en_28_dias_y_bsw_no_reproduce_bwpd():
    serie = leer_serie()
    assert contar_identidades(serie) == 28
    assert all(identidad_exacta(fila) for fila in serie)
    assert all(not bsw_reproduce_bwpd(fila) for fila in serie)
    assert particionar(5180.0, 5099.4) == 80.60000000000036
    expresiones = formulas_bopd()
    assert len(expresiones) == 28
    assert all(expr.startswith("=") and "-C" in expr for expr in expresiones)


def test_el_motor_reproduce_el_dia_de_referencia_sin_inventar_bomba():
    salida = evaluar_solicitud({"dataset_id": "RB-IA-2191", "pozo_id": "RB-IA-2191", "variables": []})
    assert salida["estado_evaluacion"] == "completada_preliminar"
    assert salida["recomendacion_operacional_autorizada"] is False
    assert salida["resultados_sin_regla"] is True
    assert salida["coincidencia_dia_referencia"] is True
    valores = salida["modelos"][0]["valores"]
    assert abs(valores["bopd"] - 80.6) < 1e-9
    assert valores["dias_serie"] == 28
    assert valores["dias_identidad_exacta"] == 28
    assert "caudal_a_producir_bfpd" not in valores
    assert "pip_ft" not in valores


def test_un_caudal_nuevo_recalcula_bopd_y_deja_de_coincidir():
    salida = evaluar_solicitud({
        "dataset_id": "RB-IA-2191",
        "pozo_id": "RB-IA-2191",
        "variables": [
            {"nombre": "bfpd", "valor": 5000, "unidad": "BFPD"},
            {"nombre": "bwpd", "valor": 4900, "unidad": "BFPD"},
        ],
    })
    valores = salida["modelos"][0]["valores"]
    assert valores["bopd"] == 100
    assert salida["coincidencia_dia_referencia"] is False


def test_rechaza_otro_pozo_entrada_ajena_y_bwpd_mayor():
    assert evaluar_solicitud({"pozo_id": "RB-1521"})["estado_evaluacion"] == "entrada_invalida"
    salida = evaluar_solicitud({
        "pozo_id": "RB-IA-2191",
        "variables": [{"nombre": "frecuencia_hz", "valor": 60, "unidad": "Hz"}],
    })
    assert salida["estado_evaluacion"] == "entrada_invalida"
    salida = evaluar_solicitud({
        "pozo_id": "RB-IA-2191",
        "variables": [
            {"nombre": "bfpd", "valor": 100, "unidad": "BFPD"},
            {"nombre": "bwpd", "valor": 200, "unidad": "BFPD"},
        ],
    })
    assert salida["estado_evaluacion"] == "entrada_invalida"
