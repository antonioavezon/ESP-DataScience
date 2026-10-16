"""Particiones de la fase A y métricas, sin entrenar modelos."""

import os
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from esp_datascience.metricas import (
    coeficiente_determinacion,
    error_absoluto_medio,
    raiz_error_cuadratico_medio,
    sesgo_medio,
)
from esp_datascience.particiones import (
    COLUMNAS_PROHIBIDAS,
    PREDICTORES_MAPPING,
    PREDICTORES_SURGING,
    SEMILLA,
    entradas_mapping,
    entradas_surging,
    marcar_pliegues,
    pliegues_internos,
    resumen_pliegues_externos,
)
from esp_datascience.rutas import huella_sha256

HUELLAS = {
    "data/raw/mapping.xlsx": "3b933ca84911484f5d912a44b025f5589abaf5ebc2b0426bf80c083869762bda",
    "data/raw/surging.xlsx": "acdcc6c5fc3d8969280c8712c45657fbb863f163a60829584fece5abf75f28cd",
    "data/processed/mapping_long.csv": "ff68e36703d3d3901b8bd964008c49b062afa9d89a817b9d66e7849f9b400648",
    "data/processed/surging_long.csv": "f58e8e2cac74acdf2081479ec8769422f39c4e4665f5b3ff472df4a70b15bd96",
}


class IntegridadYParticiones(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.chdir(RAIZ)
        for relativo, esperada in HUELLAS.items():
            obtenida = huella_sha256(RAIZ / relativo)
            if obtenida != esperada:
                raise AssertionError(relativo)
        cls.mapping = pd.read_csv(RAIZ / "data/processed/mapping_long.csv")
        cls.surging = pd.read_csv(RAIZ / "data/processed/surging_long.csv")

    def test_conteos_publicados(self):
        self.assertEqual(len(self.mapping), 570)
        self.assertEqual(len(self.surging), 387)

    def test_mapping_tres_pliegues_sin_fuga(self):
        marcada = marcar_pliegues(self.mapping, "mapping")
        otra = marcar_pliegues(self.mapping, "mapping")
        self.assertTrue(marcada["pliegue"].equals(otra["pliegue"]))
        resumen = resumen_pliegues_externos(marcada)
        self.assertEqual(list(resumen["pliegue"]), [0, 1, 2])
        self.assertTrue(resumen["ambas_velocidades"].all())
        self.assertTrue(resumen["tres_presiones"].all())
        self.assertTrue(resumen["condiciones_estimables"].all())
        self.assertEqual(int(resumen["n_curvas_prueba"].sum()), 30)
        self.assertEqual(marcada["curva_id"].nunique(), 30)
        self.assertTrue(set(PREDICTORES_MAPPING).isdisjoint(COLUMNAS_PROHIBIDAS))

    def test_surging_tres_pliegues_sin_fuga(self):
        marcada = marcar_pliegues(self.surging, "surging")
        resumen = resumen_pliegues_externos(marcada)
        self.assertEqual(int(resumen["n_curvas_prueba"].sum()), 18)
        self.assertTrue(resumen["condiciones_estimables"].all())
        self.assertTrue(resumen["ambas_velocidades"].all())
        self.assertTrue(set(PREDICTORES_SURGING).isdisjoint(COLUMNAS_PROHIBIDAS))

    def test_internos_conservan_condiciones(self):
        mapping = marcar_pliegues(self.mapping, "mapping")
        surging = marcar_pliegues(self.surging, "surging")
        for pliegue in (0, 1, 2):
            interno_m = pliegues_internos(mapping, pliegue, 4)
            interno_s = pliegues_internos(surging, pliegue, 3)
            self.assertTrue(interno_m["condiciones_estimables"].all())
            self.assertTrue(interno_s["condiciones_estimables"].all())
            self.assertTrue(interno_m["ambas_velocidades"].all())
            self.assertTrue(interno_s["tres_presiones"].all())

    def test_qgd_no_se_imputa(self):
        entradas = entradas_mapping(self.mapping)
        agua = entradas["es_monofasica"]
        self.assertEqual(int(agua.sum()), 87)
        self.assertTrue(entradas.loc[agua, "qgd"].isna().all())
        self.assertTrue(entradas.loc[~agua, "qgd"].notna().all())
        self.assertEqual(list(entradas.columns), list(PREDICTORES_MAPPING))
        sur = entradas_surging(self.surging)
        self.assertEqual(len(sur), 387)

    def test_semilla_reproducible(self):
        primero = np.random.default_rng(SEMILLA).integers(0, 1000, size=4)
        segundo = np.random.default_rng(SEMILLA).integers(0, 1000, size=4)
        self.assertTrue(np.array_equal(primero, segundo))

    def test_metricas_conocidas(self):
        self.assertEqual(error_absoluto_medio([1.0, 3.0], [1.0, 1.0]), 1.0)
        self.assertEqual(raiz_error_cuadratico_medio([0.0, 0.0], [0.0, 2.0]), 2.0 ** 0.5)
        self.assertEqual(sesgo_medio([1.0, 1.0], [2.0, 2.0]), 1.0)
        self.assertEqual(coeficiente_determinacion([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]), 1.0)
        with self.assertRaises(ValueError):
            coeficiente_determinacion([2.0, 2.0], [2.0, 3.0])


if __name__ == "__main__":
    unittest.main()
