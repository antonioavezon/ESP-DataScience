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
    diferencia_pareada,
    error_absoluto_medio,
    media_por_curva,
    metrica_por_curva,
    raiz_error_cuadratico_medio,
    sesgo_medio,
)
from esp_datascience.particiones import (
    COLUMNAS_PROHIBIDAS,
    PREDICTORES_MAPPING,
    PREDICTORES_SURGING,
    SEMILLA,
    auditar_particiones,
    entradas_mapping,
    entradas_surging,
    marcar_pliegues,
    pliegues_internos,
    qgd_tecnico,
    resumen_pliegues_externos,
)
from esp_datascience.protocolo import (
    COMPARACION,
    CONGELADO,
    CORTES_INTERNOS,
    METRICA_PRINCIPAL,
    VERSION,
    condiciones_no_vistas,
    huella_pliegues,
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

    def test_auditoria_y_huella_congelada(self):
        self.assertEqual(auditar_particiones(self.mapping, "mapping", 4)["n_curvas"], 30)
        self.assertEqual(auditar_particiones(self.surging, "surging", 3)["n_curvas"], 18)
        self.assertEqual(
            huella_pliegues(self.mapping, "mapping"),
            "f35be865a01a6255cc08afdccb96863184ad394a550d9a5249d42b4041a8d948",
        )
        self.assertEqual(
            huella_pliegues(self.surging, "surging"),
            "71c4818c4b3a5bce0d363c5df658e04141ce1c1301e72f754d5805a52c9dc742",
        )
        self.assertEqual(huella_pliegues(self.mapping, "mapping"), huella_pliegues(self.mapping, "mapping"))
        self.assertTrue(CONGELADO)
        self.assertEqual(VERSION, "2.14-A")
        self.assertEqual(CORTES_INTERNOS, {"mapping": 4, "surging": 3})
        self.assertIn("MAE", METRICA_PRINCIPAL)
        self.assertIn("pareada", COMPARACION)

    def test_peso_igual_por_curva(self):
        medicion = [0.0, 0.0, 0.0]
        prediccion = [10.0, 0.0, 0.0]
        curvas = ["a", "b", "b"]
        self.assertAlmostEqual(error_absoluto_medio(medicion, prediccion), 10.0 / 3.0)
        self.assertEqual(media_por_curva(medicion, prediccion, curvas, error_absoluto_medio), 5.0)
        por_curva = metrica_por_curva(medicion, prediccion, curvas, error_absoluto_medio)
        otra = por_curva.copy()
        otra.index = ["a", "c"]
        with self.assertRaises(ValueError):
            diferencia_pareada(por_curva, otra)
        self.assertEqual(float(diferencia_pareada(por_curva, por_curva).sum()), 0.0)

    def test_qgd_tecnico_no_es_medicion(self):
        ausencias = int(self.mapping["qgd"].isna().sum())
        tecnico = qgd_tecnico(self.mapping["qgd"], self.mapping["condicion"].eq("Single Phase"))
        self.assertEqual(int(self.mapping["qgd"].isna().sum()), ausencias)
        self.assertEqual(ausencias, 87)
        self.assertEqual(int((tecnico == 0).sum()), 87)
        self.assertTrue(tecnico.loc[~self.mapping["condicion"].eq("Single Phase").to_numpy()].notna().all())

    def test_condiciones_no_vistas_no_se_ejecutan(self):
        mapping = condiciones_no_vistas(self.mapping, "mapping")
        surging = condiciones_no_vistas(self.surging, "surging")
        self.assertTrue((~mapping["ejecutada"]).all())
        self.assertTrue((~mapping["es_la_evaluacion_principal"]).all())
        self.assertTrue((~mapping["la_recta_por_etiqueta_puede_predecirla"]).all())
        agua = mapping[mapping["etiqueta_reservada"].eq("Single Phase")].iloc[0]
        self.assertEqual(agua["posicion_numerica"], "sin valor numérico de gas")
        borde = mapping[mapping["etiqueta_reservada"].eq("Qgd=0.05")].iloc[0]
        self.assertEqual(borde["posicion_numerica"], "en el borde de los valores del archivo")
        interior = mapping[mapping["etiqueta_reservada"].eq("Qgd=0.02")].iloc[0]
        self.assertEqual(interior["posicion_numerica"], "entre otros valores del archivo")
        self.assertEqual(surging["que_probaria"].str.contains("no es un GVF0").all(), True)
        self.assertEqual(len(surging), 3)
        self.assertEqual(int(self.mapping["qgd"].isna().sum()), 87)



if __name__ == "__main__":
    unittest.main()
