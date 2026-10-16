"""Fase B: M1 y M2, sin cambiar las particiones de 2.14-A."""

import os
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from esp_datascience.entrenamiento import (
    ALPHAS,
    GRADO_POLINOMIO,
    HUELLAS_PLIEGUES,
    ORDEN_M2,
    elegir_alpha,
    evaluar_protocolo,
    matriz_entradas,
    pipeline_m1,
    pipeline_m2,
)
from esp_datascience.metricas import error_absoluto_medio, media_por_curva
from esp_datascience.particiones import marcar_pliegues
from esp_datascience.protocolo import VERSION, huella_pliegues
from esp_datascience.rutas import huella_sha256

HUELLAS_ARCHIVO = {
    "data/raw/mapping.xlsx": "3b933ca84911484f5d912a44b025f5589abaf5ebc2b0426bf80c083869762bda",
    "data/raw/surging.xlsx": "acdcc6c5fc3d8969280c8712c45657fbb863f163a60829584fece5abf75f28cd",
    "data/processed/mapping_long.csv": "ff68e36703d3d3901b8bd964008c49b062afa9d89a817b9d66e7849f9b400648",
    "data/processed/surging_long.csv": "f58e8e2cac74acdf2081479ec8769422f39c4e4665f5b3ff472df4a70b15bd96",
}


class EntrenamientoFaseB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.chdir(RAIZ)
        for relativo, esperada in HUELLAS_ARCHIVO.items():
            if huella_sha256(RAIZ / relativo) != esperada:
                raise AssertionError(relativo)
        cls.mapping = pd.read_csv(RAIZ / "data/processed/mapping_long.csv")
        cls.surging = pd.read_csv(RAIZ / "data/processed/surging_long.csv")
        cls.qgd_ausente = int(cls.mapping["qgd"].isna().sum())
        cls.resultado_mapping = evaluar_protocolo(cls.mapping, "mapping")
        cls.resultado_surging = evaluar_protocolo(cls.surging, "surging")

    def test_protocolo_congelado(self):
        self.assertEqual(VERSION, "2.14-A")
        self.assertEqual(GRADO_POLINOMIO, 2)
        self.assertEqual(ALPHAS, (0.01, 0.1, 1.0, 10.0, 100.0))
        self.assertEqual(huella_pliegues(self.mapping, "mapping"), HUELLAS_PLIEGUES["mapping"])
        self.assertEqual(huella_pliegues(self.surging, "surging"), HUELLAS_PLIEGUES["surging"])
        self.assertEqual(self.qgd_ausente, 87)
        self.assertEqual(int(self.mapping["qgd"].isna().sum()), 87)
        for relativo, esperada in HUELLAS_ARCHIVO.items():
            self.assertEqual(huella_sha256(RAIZ / relativo), esperada)

    def test_resultados_reproducibles(self):
        otra = evaluar_protocolo(self.mapping, "mapping")
        self.assertTrue(
            np.allclose(
                self.resultado_mapping["predicciones"]["prediccion_m2"],
                otra["predicciones"]["prediccion_m2"],
            )
        )
        self.assertTrue(self.resultado_mapping["alphas"]["alpha"].equals(otra["alphas"]["alpha"]))
        esperados = {
            ("mapping", "M1"): 3.998654558642768,
            ("mapping", "M2"): 1.364197299900999,
            ("surging", "M1"): 2.31240277528348,
            ("surging", "M2"): 1.1137313367403104,
        }
        for resultado in (self.resultado_mapping, self.resultado_surging):
            for _, fila in resultado["externo"].iterrows():
                clave = (fila["protocolo"], fila["modelo"])
                self.assertAlmostEqual(fila["mae_curva"], esperados[clave], places=6)

    def test_una_prediccion_externa_por_fila(self):
        for tabla, resultado in (
            (self.mapping, self.resultado_mapping),
            (self.surging, self.resultado_surging),
        ):
            pred = resultado["predicciones"]
            self.assertEqual(len(pred), len(tabla))
            self.assertFalse(pred.index.duplicated().any())
            self.assertEqual(int(pred["prediccion_m1"].isna().sum()), 0)
            self.assertEqual(int(pred["prediccion_m2"].isna().sum()), 0)
            self.assertTrue(np.allclose(pred["medicion"], tabla["dp2_3_psi"]))
            self.assertEqual(set(pred["pliegue"]), {0, 1, 2})
            for modelo in ("M1", "M2"):
                cifras = resultado["externo"].set_index("modelo").loc[modelo]
                columna = "prediccion_m1" if modelo == "M1" else "prediccion_m2"
                self.assertAlmostEqual(
                    cifras["mae_curva"],
                    media_por_curva(pred["medicion"], pred[columna], pred["curva_id"], error_absoluto_medio),
                )

    def test_alpha_no_usa_la_prueba_externa(self):
        marcada = marcar_pliegues(self.mapping, "mapping")
        alpha, _ = elegir_alpha(marcada, "mapping", 0)
        alterada = marcada.copy()
        alterada.loc[alterada["pliegue"].eq(0), "dp2_3_psi"] = -999.0
        alpha_alterada, _ = elegir_alpha(alterada, "mapping", 0)
        self.assertEqual(alpha, alpha_alterada)
        self.assertEqual(list(self.resultado_mapping["alphas"]["alpha"]), [0.1, 0.1, 0.1])
        self.assertEqual(list(self.resultado_surging["alphas"]["alpha"]), [0.01, 1.0, 0.01])
        with self.assertRaises(ValueError):
            pipeline_m2("mapping", 0.3)

    def test_escala_no_ve_la_prueba(self):
        marcada = marcar_pliegues(self.mapping, "mapping")
        entrena = marcada["pliegue"] != 0
        prueba = marcada["pliegue"] == 0
        Xtr = matriz_entradas(marcada.loc[entrena], "mapping")
        ytr = marcada.loc[entrena, "dp2_3_psi"].to_numpy(dtype=float)
        modelo = pipeline_m2("mapping", 1.0)
        self.assertEqual(tuple(modelo.named_steps), ORDEN_M2)
        self.assertEqual(modelo.named_steps["polinomio"].degree, 2)
        self.assertFalse(modelo.named_steps["polinomio"].include_bias)
        nombres = list(modelo.named_steps)
        self.assertLess(nombres.index("polinomio"), nombres.index("escala"))
        self.assertLess(nombres.index("escala"), nombres.index("cresta"))
        modelo.fit(Xtr, ytr)
        media = modelo.named_steps["escala"].mean_.copy()
        visto = int(modelo.named_steps["escala"].n_samples_seen_)
        self.assertEqual(visto, len(Xtr))
        self.assertNotIn("curva_id", modelo.named_steps["preparar"].nombres_salida_)
        self.assertNotIn("origen_velocidad", modelo.named_steps["preparar"].nombres_salida_)
        self.assertIn("qgd_tecnico", modelo.named_steps["preparar"].nombres_salida_)
        Xte = matriz_entradas(marcada.loc[prueba], "mapping").copy()
        Xte["ql_bpd"] = 1.0e12
        modelo.predict(Xte)
        self.assertTrue(np.allclose(media, modelo.named_steps["escala"].mean_))
        self.assertEqual(int(modelo.named_steps["escala"].n_samples_seen_), visto)
        self.assertEqual(int(marcada.loc[prueba, "qgd"].isna().sum()), int(self.mapping.loc[prueba, "qgd"].isna().sum()))
        junto = pd.concat([Xtr, Xte], axis=0)
        yjunto = np.concatenate([ytr, marcada.loc[prueba, "dp2_3_psi"].to_numpy(dtype=float)])
        otro = pipeline_m2("mapping", 1.0)
        otro.fit(junto, yjunto)
        self.assertFalse(np.allclose(media, otro.named_steps["escala"].mean_))
        self.assertEqual(tuple(pipeline_m1("surging").named_steps), ("preparar", "linea"))

    def test_delta_es_m2_menos_m1(self):
        diferencias = self.resultado_mapping["diferencias"]
        self.assertTrue(np.allclose(diferencias["delta_mae"], diferencias["mae_m2"] - diferencias["mae_m1"]))
        self.assertEqual(int((diferencias["delta_mae"] < 0).sum()), 29)
        self.assertEqual(int((self.resultado_surging["diferencias"]["delta_mae"] < 0).sum()), 17)


if __name__ == "__main__":
    unittest.main()
