"""Fase C: M3, M4 y M5, sin cambiar el protocolo 2.14-A ni M1 y M2.

Los cuadros sintéticos de este archivo no son datos de la bomba.
"""

import os
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from esp_datascience.entrenamiento import HUELLAS_PLIEGUES, evaluar_protocolo
from esp_datascience.fase_c import (
    N_ESTIMADORES,
    _columnas_ajustables,
    _interpolar_agua,
    diferencias_sobre_curvas_comunes,
    evaluar_m3,
    evaluar_m4,
    evaluar_m5,
    factibilidad_m3,
    factibilidad_m5,
    metricas_de_columna,
    pipeline_m4,
)
from esp_datascience.metricas import error_absoluto_medio, media_por_curva, metrica_por_curva
from esp_datascience.particiones import marcar_pliegues
from esp_datascience.protocolo import VERSION, huella_pliegues
from esp_datascience.rutas import huella_sha256

HUELLAS_ARCHIVO = {
    "data/raw/mapping.xlsx": "3b933ca84911484f5d912a44b025f5589abaf5ebc2b0426bf80c083869762bda",
    "data/raw/surging.xlsx": "acdcc6c5fc3d8969280c8712c45657fbb863f163a60829584fece5abf75f28cd",
    "data/processed/mapping_long.csv": "ff68e36703d3d3901b8bd964008c49b062afa9d89a817b9d66e7849f9b400648",
    "data/processed/surging_long.csv": "f58e8e2cac74acdf2081479ec8769422f39c4e4665f5b3ff472df4a70b15bd96",
}
OBJETIVO = "dp2_3_psi"


class FaseC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.chdir(RAIZ)
        for relativo, esperada in HUELLAS_ARCHIVO.items():
            if huella_sha256(RAIZ / relativo) != esperada:
                raise AssertionError(relativo)
        cls.mapping = pd.read_csv(RAIZ / "data/processed/mapping_long.csv")
        cls.surging = pd.read_csv(RAIZ / "data/processed/surging_long.csv")
        cls.base_mapping = evaluar_protocolo(cls.mapping, "mapping")
        cls.base_surging = evaluar_protocolo(cls.surging, "surging")
        cls.m3_mapping = evaluar_m3(cls.mapping, "mapping")
        cls.m3_surging = evaluar_m3(cls.surging, "surging")
        cls.m4_mapping = evaluar_m4(cls.mapping, "mapping")
        cls.m4_surging = evaluar_m4(cls.surging, "surging")
        cls.m5 = evaluar_m5(cls.mapping)

    def test_huellas_y_pliegues(self):
        self.assertEqual(VERSION, "2.14-A")
        self.assertEqual(huella_pliegues(self.mapping, "mapping"), HUELLAS_PLIEGUES["mapping"])
        self.assertEqual(huella_pliegues(self.surging, "surging"), HUELLAS_PLIEGUES["surging"])
        for relativo, esperada in HUELLAS_ARCHIVO.items():
            self.assertEqual(huella_sha256(RAIZ / relativo), esperada)

    def test_m1_y_m2_se_conservan(self):
        publicados = {("mapping", "M1"): 3.999, ("mapping", "M2"): 1.364, ("surging", "M1"): 2.312, ("surging", "M2"): 1.114}
        for resultado, protocolo in ((self.base_mapping, "mapping"), (self.base_surging, "surging")):
            for _, fila in resultado["externo"].iterrows():
                self.assertEqual(round(float(fila["mae_curva"]), 3), publicados[(protocolo, fila["modelo"])])

    def test_cobertura_completa_de_m3_y_m4(self):
        for resultado, n_curvas, n_filas in (
            (self.m3_mapping, 30, 570),
            (self.m3_surging, 18, 387),
            (self.m4_mapping, 30, 570),
            (self.m4_surging, 18, 387),
        ):
            cifras = resultado["metricas"]
            self.assertEqual(cifras["n_curvas_cubiertas"], n_curvas)
            self.assertEqual(cifras["n_filas_en_el_mae"], n_filas)
            self.assertFalse(resultado["predicciones"].filter(like="prediccion_").isna().any().any())

    def test_m3_no_usa_la_presion_de_prueba(self):
        marcada = marcar_pliegues(self.mapping, "mapping")
        alterada = self.mapping.copy()
        alterada.loc[marcada["pliegue"].eq(0).to_numpy(), OBJETIVO] = 80.0
        otra = evaluar_m3(alterada, "mapping")
        original = self.m3_mapping["predicciones"]
        nueva = otra["predicciones"]
        mascara = original["pliegue"].eq(0)
        self.assertTrue(np.allclose(original.loc[mascara, "prediccion_m3"], nueva.loc[mascara, "prediccion_m3"]))

    def test_m3_no_mezcla_condiciones(self):
        alterada = self.mapping.copy()
        alterada.loc[alterada["condicion"].eq("Single Phase"), OBJETIVO] = 40.0
        otra = evaluar_m3(alterada, "mapping")
        gas = self.mapping["condicion"].ne("Single Phase")
        agua = ~gas
        self.assertTrue(
            np.allclose(
                self.m3_mapping["predicciones"].loc[gas, "prediccion_m3"],
                otra["predicciones"].loc[gas, "prediccion_m3"],
            )
        )
        self.assertFalse(
            np.allclose(
                self.m3_mapping["predicciones"].loc[agua, "prediccion_m3"],
                otra["predicciones"].loc[agua, "prediccion_m3"],
            )
        )
        for fila in self.m3_mapping["detalle"]:
            self.assertNotIn("curva_id", fila["predictores"])
            self.assertNotIn("qgd", fila["predictores"])
            self.assertNotIn("es_monofasica", fila["predictores"])

    def test_factibilidad_externa_sin_respaldo_global(self):
        for tabla, protocolo in ((self.mapping, "mapping"), (self.surging, "surging")):
            externo = factibilidad_m3(tabla, protocolo)
            externo = externo[externo["alcance"].eq("externo")]
            self.assertTrue(bool(externo["estimable"].all()))
            self.assertGreater(int(externo["presiones_de_prueba_ausentes"].map(len).gt(0).sum()), 0)

    def test_m4_elige_sin_mirar_la_prueba_y_se_repite(self):
        self.assertEqual(N_ESTIMADORES, 100)
        with self.assertRaises(ValueError):
            pipeline_m4("mapping", 9, 3)
        marcada = marcar_pliegues(self.mapping, "mapping")
        alterada = self.mapping.copy()
        alterada.loc[marcada["pliegue"].eq(0).to_numpy(), OBJETIVO] = 1.0
        otra = evaluar_m4(alterada, "mapping")
        hiper = self.m4_mapping["hiperparametros"].set_index("pliegue").loc[0]
        hiper_nueva = otra["hiperparametros"].set_index("pliegue").loc[0]
        self.assertEqual(int(hiper["max_depth"]), int(hiper_nueva["max_depth"]))
        self.assertEqual(int(hiper["min_samples_leaf"]), int(hiper_nueva["min_samples_leaf"]))
        mascara = self.m4_mapping["predicciones"]["pliegue"].eq(0)
        self.assertTrue(
            np.allclose(
                self.m4_mapping["predicciones"].loc[mascara, "prediccion_m4"],
                otra["predicciones"].loc[mascara, "prediccion_m4"],
            )
        )
        repetida = evaluar_m4(self.mapping, "mapping")
        self.assertTrue(
            np.allclose(
                self.m4_mapping["predicciones"]["prediccion_m4"],
                repetida["predicciones"]["prediccion_m4"],
            )
        )
        self.assertTrue(self.m4_mapping["hiperparametros"]["max_depth"].equals(repetida["hiperparametros"]["max_depth"]))

    def test_m5_no_lee_el_agua_de_prueba(self):
        marcada = marcar_pliegues(self.mapping, "mapping")
        agua_de_prueba = marcada["condicion"].eq("Single Phase") & marcada["pliegue"].eq(0)
        alterada = self.mapping.copy()
        alterada.loc[agua_de_prueba.to_numpy(), OBJETIVO] = 90.0
        otra = evaluar_m5(alterada)
        mascara = marcada["pliegue"].eq(0) & marcada["condicion"].ne("Single Phase")
        self.assertTrue(
            np.allclose(
                self.m5["predicciones"].loc[mascara, "prediccion_m5"],
                otra["predicciones"].loc[mascara, "prediccion_m5"],
                equal_nan=True,
            )
        )
        agua = self.m5["predicciones"]["condicion"].eq("Single Phase")
        self.assertEqual(int(self.m5["predicciones"].loc[agua, "prediccion_m5"].notna().sum()), 0)
        relacion = factibilidad_m5(self.mapping)
        self.assertTrue(bool((relacion["su_agua_esta_en_entrenamiento"] == relacion["curvas_gas_de_prueba"]).all()))
        self.assertTrue(bool((relacion["agua_reservada_en_la_prueba"] > 0).all()))
        cubiertas = set(self.m5["mae_por_curva"].index)
        self.assertLess(len(cubiertas), 30)
        self.assertGreater(len(cubiertas), 0)
        for curva in cubiertas:
            agua_id = curva.rsplit("|", 1)[0] + "|Single Phase"
            pliegue_gas = int(marcada.loc[marcada["curva_id"].eq(curva), "pliegue"].iloc[0])
            pliegue_agua = int(marcada.loc[marcada["curva_id"].eq(agua_id), "pliegue"].iloc[0])
            self.assertNotEqual(pliegue_gas, pliegue_agua)

    def test_metricas_y_comparacion_pareada(self):
        pred = self.m3_mapping["predicciones"]
        rehecha = metricas_de_columna(pred, "prediccion_m3", "mapping", "M3")
        self.assertAlmostEqual(rehecha["mae_curva"], self.m3_mapping["metricas"]["mae_curva"])
        mae_m1 = metrica_por_curva(
            self.base_mapping["predicciones"]["medicion"],
            self.base_mapping["predicciones"]["prediccion_m1"],
            self.base_mapping["predicciones"]["curva_id"],
            error_absoluto_medio,
        )
        delta = diferencias_sobre_curvas_comunes(mae_m1, self.m3_mapping["mae_por_curva"])
        self.assertEqual(list(delta.index), list(mae_m1.index))
        with self.assertRaises(ValueError):
            diferencias_sobre_curvas_comunes(mae_m1, self.m5["mae_por_curva"])
        comun = diferencias_sobre_curvas_comunes(mae_m1, self.m5["mae_por_curva"], exigir_las_mismas=False)
        self.assertEqual(set(comun.index), set(self.m5["mae_por_curva"].index))


class SinteticosQueNoSonLaBomba(unittest.TestCase):
    def test_un_predictor_constante_no_recibe_coeficiente(self):
        grupo = pd.DataFrame(
            {
                "ql_bpd": [100.0, 200.0, 300.0, 400.0],
                "velocidad_rpm": [1800, 1800, 1800, 1800],
                "psep_psig": [50.0, 50.0, 50.0, 50.0],
            }
        )
        self.assertEqual(_columnas_ajustables(grupo, "mapping"), ["ql_bpd"])
        grupo["ql_bpd"] = 100.0
        grupo["velocidad_rpm"] = [1800, 1800, 3500, 3500]
        self.assertEqual(_columnas_ajustables(grupo, "mapping"), [])

    def test_la_interpolacion_no_sale_del_tramo(self):
        agua = pd.DataFrame({"ql_bpd": [0.0, 10.0], "dp2_3_psi": [20.0, 10.0]})
        self.assertIsNone(_interpolar_agua(agua, -0.1))
        self.assertIsNone(_interpolar_agua(agua, 10.1))
        self.assertAlmostEqual(_interpolar_agua(agua, 5.0), 15.0)
        self.assertAlmostEqual(_interpolar_agua(agua, 0.0), 20.0)

    def test_el_peso_por_curva_no_sigue_el_numero_de_filas(self):
        pred = pd.DataFrame(
            {
                "curva_id": ["a", "b", "b"],
                "medicion": [10.0, 0.0, 0.0],
                "prediccion": [0.0, 0.0, 0.0],
            }
        )
        cifras = metricas_de_columna(pred, "prediccion", "sintetico", "S")
        self.assertAlmostEqual(cifras["mae_curva"], 5.0)
        self.assertAlmostEqual(cifras["mae_fila"], 10.0 / 3.0)
        self.assertAlmostEqual(
            media_por_curva(pred["medicion"], pred["prediccion"], pred["curva_id"], error_absoluto_medio),
            5.0,
        )
