"""Equivalencia entre src/esp_datascience y los CSV de la actividad 2.12.

No reescribe data/processed ni data/raw. Compara en memoria el texto que
producirían las mismas funciones con el archivo ya publicado.
"""

import os
import sys
import unittest
from io import StringIO
from pathlib import Path

RAIZ_PRUEBA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_PRUEBA / "src"))

import pandas as pd

from esp_datascience.lectura import es_numero, psep_de_hoja
from esp_datascience.normalizacion import (
    normalizar_mapping,
    normalizar_surging,
    velocidad_segun_diseno,
)
from esp_datascience.rutas import encontrar_raiz_laboratorio, huella_sha256
from esp_datascience.validacion import comprobar_conteos_publicados

HUELLAS_EXCEL = {
    "data/raw/mapping.xlsx": "3b933ca84911484f5d912a44b025f5589abaf5ebc2b0426bf80c083869762bda",
    "data/raw/surging.xlsx": "acdcc6c5fc3d8969280c8712c45657fbb863f163a60829584fece5abf75f28cd",
}
HUELLAS_CSV = {
    "data/processed/mapping_long.csv": "ff68e36703d3d3901b8bd964008c49b062afa9d89a817b9d66e7849f9b400648",
    "data/processed/surging_long.csv": "f58e8e2cac74acdf2081479ec8769422f39c4e4665f5b3ff472df4a70b15bd96",
}
FILAS_ESPERADAS = {
    "data/processed/mapping_long.csv": 570,
    "data/processed/surging_long.csv": 387,
}
ENTEROS = [
    "psep_psig",
    "fila",
    "columna_condicion",
    "columna_dp",
    "velocidad_rpm",
    "fila_celda_velocidad",
    "columna_celda_velocidad",
    "valor_celda_velocidad",
]


def _texto_csv(tabla: pd.DataFrame, columna_extra: str) -> str:
    copia = tabla.copy()
    for columna in ENTEROS:
        if columna in copia.columns:
            copia[columna] = copia[columna].astype("Int64")
    copia[columna_extra] = copia[columna_extra].astype("Int64")
    buffer = StringIO()
    copia.to_csv(buffer, index=False, na_rep="")
    return buffer.getvalue()


def _construir(raiz: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    hojas = ("50psig", "100psig", "150psig")
    mapping = pd.ExcelFile(raiz / "data" / "raw" / "mapping.xlsx")
    surging = pd.ExcelFile(raiz / "data" / "raw" / "surging.xlsx")
    partes_mapping = []
    for hoja in hojas:
        parte, _huecos = normalizar_mapping(pd.read_excel(mapping, sheet_name=hoja, header=None), hoja)
        partes_mapping.append(parte)
    partes_surging = []
    for hoja in hojas:
        parte, _huecos = normalizar_surging(pd.read_excel(surging, sheet_name=hoja, header=None), hoja)
        partes_surging.append(parte)
    return pd.concat(partes_mapping, ignore_index=True), pd.concat(partes_surging, ignore_index=True)


class EquivalenciaNormalizacion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.chdir(RAIZ_PRUEBA)
        cls.raiz = encontrar_raiz_laboratorio()
        cls.huellas_antes = {
            relativo: huella_sha256(cls.raiz / relativo)
            for relativo in (*HUELLAS_EXCEL, *HUELLAS_CSV)
        }

    def test_huellas_publicadas(self):
        for relativo, esperada in {**HUELLAS_EXCEL, **HUELLAS_CSV}.items():
            self.assertEqual(self.huellas_antes[relativo], esperada, relativo)

    def test_reglas_de_diseno_y_presion(self):
        self.assertEqual(
            velocidad_segun_diseno({"Qgd=0.005", "Qgd=0.01", "Qgd=0.015"}),
            1800,
        )
        self.assertEqual(
            velocidad_segun_diseno({"Qgd=0.01", "Qgd=0.02", "Qgd=0.03", "Qgd=0.04", "Qgd=0.05"}),
            3500,
        )
        self.assertEqual(psep_de_hoja("100psig"), 100)
        self.assertTrue(es_numero(1800))
        self.assertFalse(es_numero(float("nan")))

    def test_modulos_reproducen_los_csv(self):
        mapping, surging = _construir(self.raiz)
        self.assertEqual(len(mapping), 570)
        self.assertEqual(len(surging), 387)
        comprobar_conteos_publicados(mapping, surging)
        generado = {
            "data/processed/mapping_long.csv": _texto_csv(mapping, "columna_caudal"),
            "data/processed/surging_long.csv": _texto_csv(surging, "columna_gvf"),
        }
        for relativo, texto in generado.items():
            publicado = (self.raiz / relativo).read_text(encoding="utf-8")
            self.assertEqual(texto, publicado, relativo)
            lineas = [linea for linea in texto.splitlines() if linea]
            self.assertEqual(len(lineas) - 1, FILAS_ESPERADAS[relativo], relativo)

    def test_los_archivos_no_cambiaron(self):
        mapping, surging = _construir(self.raiz)
        comprobar_conteos_publicados(mapping, surging)
        for relativo, anterior in self.huellas_antes.items():
            actual = huella_sha256(self.raiz / relativo)
            self.assertEqual(actual, anterior, relativo)


if __name__ == "__main__":
    unittest.main()
