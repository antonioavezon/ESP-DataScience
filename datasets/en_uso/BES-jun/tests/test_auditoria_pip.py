"""Auditoría de PIP contra el Excel. No cambia la fórmula de la celda.

Los esperados físicos están escritos aquí. Reproducir la caché no se toma
como validación de la admisión.
"""

import hashlib
import re
from pathlib import Path

import pytest
from openpyxl import load_workbook

from evaluacion.contratos import VERSION_CONTRATO, errores_de_salida
from evaluacion.motor import evaluar_solicitud
from modelo_deterministico.balance_bes_jun import evaluar_balance, pip_en_ft, thd_total_ft

# Raíz del repo (…/datasets/en_uso/BES-jun/tests → 4 niveles arriba).
_RAIZ_REPO = Path(__file__).resolve().parents[4]
ORIGINAL = _RAIZ_REPO / "fuentes" / "originales" / "Copia de FINAL BES-jun.xlsx"
HUELLA = "ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85"
FORMULA_PIP = re.compile(r"^=\(B(\d+)-\(\(C(\d+)-C(\d+)\)\*B(\d+)\)\)/B\4$")


def _celda(presion, tvd_intake, tvd_sensor, gradiente):
    return presion / gradiente + tvd_sensor - tvd_intake


def _hidrostatica(presion, tvd_intake, tvd_sensor, gradiente):
    """Profundidad positiva hacia abajo: la admisión más somera tiene menos presión."""
    return presion / gradiente - (tvd_sensor - tvd_intake)


def _fila(ws, columna, texto):
    objetivo = texto.casefold()
    for fila in range(1, ws.max_row + 1):
        valor = ws.cell(fila, columna).value
        if valor is not None and str(valor).strip().casefold() == objetivo:
            return fila
    raise AssertionError(f"no está {texto}")


@pytest.fixture(scope="module")
def libro():
    formulas = load_workbook(ORIGINAL, data_only=False)
    valores = load_workbook(ORIGINAL, data_only=True)
    yield formulas, valores
    formulas.close()
    valores.close()


def test_el_excel_original_no_cambia_de_huella():
    digest = hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
    assert digest == HUELLA


def test_cada_hoja_tiene_su_propia_celda_y_la_misma_algebra(libro):
    formulas, _valores = libro
    vistas = {}
    for nombre in formulas.sheetnames:
        ws = formulas[nombre]
        fila_pip = _fila(ws, 5, "PIP en (ft)")
        formula = ws.cell(fila_pip, 7).value
        coincidencia = FORMULA_PIP.fullmatch(formula)
        assert coincidencia, (nombre, formula)
        fila_sensor_p, fila_intake, fila_sensor_z, fila_grad = (int(g) for g in coincidencia.groups())
        assert ws.cell(fila_pip, 8).value == "ft"
        assert ws.cell(fila_sensor_p, 1).value == "Presión de Sensor"
        assert ws.cell(fila_sensor_p, 3).value == "psi"
        assert isinstance(ws.cell(fila_sensor_p, 2).value, (int, float))
        assert ws.cell(fila_intake, 1).value == "Intake"
        assert ws.cell(fila_sensor_z, 1).value == "Sensor"
        assert isinstance(ws.cell(fila_intake, 3).value, str) and "H" in ws.cell(fila_intake, 3).value
        assert isinstance(ws.cell(fila_sensor_z, 3).value, str) and "H" in ws.cell(fila_sensor_z, 3).value
        assert "B" + str(fila_intake) not in formula
        vistas[nombre] = ws.cell(fila_pip, 7).coordinate
    assert vistas["QF-554H"] == "G96"
    assert len(set(vistas.values())) > 1


def test_la_celda_reproduce_el_excel_y_no_la_hidrostatica(libro):
    formulas, valores = libro
    for nombre in formulas.sheetnames:
        ws, vs = formulas[nombre], valores[nombre]
        fila_pip = _fila(ws, 5, "PIP en (ft)")
        grupos = FORMULA_PIP.fullmatch(ws.cell(fila_pip, 7).value).groups()
        fila_p, fila_i, fila_s, fila_g = (int(g) for g in grupos)
        presion = float(vs.cell(fila_p, 2).value)
        intake = float(vs.cell(fila_i, 3).value)
        sensor = float(vs.cell(fila_s, 3).value)
        gradiente = float(vs.cell(fila_g, 2).value)
        cache = float(vs.cell(fila_pip, 7).value)
        assert sensor > intake
        assert pip_en_ft(presion, intake, sensor, gradiente) == pytest.approx(_celda(presion, intake, sensor, gradiente))
        assert pip_en_ft(presion, intake, sensor, gradiente) == pytest.approx(cache, rel=1e-9)
        assert _celda(presion, intake, sensor, gradiente) - _hidrostatica(presion, intake, sensor, gradiente) == pytest.approx(
            2 * (sensor - intake)
        )
        assert _celda(presion, intake, sensor, gradiente) > presion / gradiente
        assert _hidrostatica(presion, intake, sensor, gradiente) < presion / gradiente


def test_sensor_encima_del_intake_cambia_el_signo_de_la_correccion():
    # 100 ft más somero. La celda resta esa columna; la hidrostática la suma.
    celda = _celda(800, 2600, 2500, 0.4)
    hidro = _hidrostatica(800, 2600, 2500, 0.4)
    assert celda == pytest.approx(1900)
    assert hidro == pytest.approx(2100)
    assert pip_en_ft(800, 2600, 2500, 0.4) == pytest.approx(celda)
    assert pip_en_ft(800, 2600, 2500, 0.4) != pytest.approx(hidro)


def test_igual_profundidad_no_aplica_correccion():
    assert _celda(800, 2500, 2500, 0.4) == pytest.approx(2000)
    assert _hidrostatica(800, 2500, 2500, 0.4) == pytest.approx(2000)
    assert pip_en_ft(800, 2500, 2500, 0.4) == pytest.approx(800 / 0.4)


def test_gradiente_nulo_o_presion_faltante_no_producen_un_pip():
    with pytest.raises(ZeroDivisionError):
        pip_en_ft(732, 2653, 2678, 0)
    nulo = evaluar_balance(732, 183, 2653, 2678, 2644, 0, 1000, 2.99)
    falta = evaluar_balance(None, 183, 2653, 2678, 2644, 0.43, 1000, 2.99)
    assert nulo.estado == "no_calculable"
    assert falta.estado == "no_calculable"
    assert "pip_ft" not in nulo.resultados
    assert "pip_ft" not in falta.resultados


def test_una_unidad_distinta_de_psi_no_se_convierte(hojas=None):
    from ingesta.leer_bes_jun import leer_libro
    hojas = leer_libro()
    solicitud = {
        "dataset_id": "BES-jun",
        "pozo_id": "QF-084",
        "version_configuracion": VERSION_CONTRATO,
        "variables": [{
            "nombre": "presion_sensor_psi",
            "valor": 732,
            "unidad": "psi*ft",
            "procedencia": "operador",
        }],
    }
    resultado = evaluar_solicitud(solicitud, hojas=hojas)
    assert resultado["estado_evaluacion"] == "entrada_invalida"
    assert any(e["codigo"] == "UNIDAD_INCOMPATIBLE" and e["campo"].endswith("presion_sensor_psi") for e in resultado["errores"])
    assert resultado["modelos"] == []
    assert errores_de_salida(resultado) == []


def test_el_rotulo_psi_por_ft_esta_escrito_como_producto(libro):
    formulas, valores = libro
    for nombre in formulas.sheetnames:
        ws, vs = formulas[nombre], valores[nombre]
        fila = _fila(ws, 1, "Gradiente de Presión")
        assert ws.cell(fila, 2).value.endswith("*0.052")
        assert ws.cell(fila, 3).value == "psi*ft"
        densidad = float(vs.cell(fila - 2, 2).value)
        assert float(vs.cell(fila, 2).value) == pytest.approx(densidad * 0.052)


def test_md_y_tvd_no_son_la_misma_correccion(libro):
    formulas, valores = libro
    for nombre in formulas.sheetnames:
        ws, vs = formulas[nombre], valores[nombre]
        fila_i, fila_s = _fila(ws, 1, "Intake"), _fila(ws, 1, "Sensor")
        md = float(vs.cell(fila_s, 2).value) - float(vs.cell(fila_i, 2).value)
        tvd = float(vs.cell(fila_s, 3).value) - float(vs.cell(fila_i, 3).value)
        assert md > tvd
        assert md - tvd > 10
        formula = ws.cell(_fila(ws, 5, "PIP en (ft)"), 7).value
        assert f"C{fila_i}" in formula and f"C{fila_s}" in formula
        assert f"B{fila_i}" not in formula and f"B{fila_s}" not in formula


def test_el_thd_resta_el_pip():
    formulas, _valores = load_workbook(ORIGINAL, data_only=False), None
    try:
        for nombre in formulas.sheetnames:
            ws = formulas[nombre]
            fila_pip = _fila(ws, 5, "PIP en (ft)")
            fila_thd = _fila(ws, 5, "THD TOTAL")
            coordenada = ws.cell(fila_pip, 7).coordinate
            formula = ws.cell(fila_thd, 7).value
            assert f"-{coordenada}" in formula.replace(" ", "")
    finally:
        formulas.close()
    assert thd_total_ft(2000, 10, 20, 500) - thd_total_ft(2000, 10, 20, 501) == pytest.approx(1)
