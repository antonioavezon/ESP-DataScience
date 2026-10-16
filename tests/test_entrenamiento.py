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
    ColumnasEstructurales,
    PrepararEntradas,
    elegir_alpha,
    evaluar_protocolo,
    filas_con_prediccion_negativa,
    guardar_derivado,
    matriz_entradas,
    pipeline_m1,
    pipeline_m2,
)
from esp_datascience.metricas import (
    coeficiente_determinacion,
    error_absoluto_medio,
    media_por_curva,
    raiz_error_cuadratico_medio,
)
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
        publicados = {("mapping", "M1"): 3.999, ("mapping", "M2"): 1.364, ("surging", "M1"): 2.312, ("surging", "M2"): 1.114}
        for resultado in (self.resultado_mapping, self.resultado_surging):
            pred = resultado["predicciones"]
            for modelo, columna in (("M1", "prediccion_m1"), ("M2", "prediccion_m2")):
                fila = resultado["externo"].set_index("modelo").loc[modelo]
                mae = media_por_curva(pred["medicion"], pred[columna], pred["curva_id"], error_absoluto_medio)
                rmse = media_por_curva(pred["medicion"], pred[columna], pred["curva_id"], raiz_error_cuadratico_medio)
                rmse_global = raiz_error_cuadratico_medio(pred["medicion"], pred[columna])
                r2 = coeficiente_determinacion(pred["medicion"], pred[columna])
                self.assertAlmostEqual(fila["mae_curva"], mae)
                self.assertAlmostEqual(fila["rmse_curva"], rmse)
                self.assertAlmostEqual(fila["rmse_fila"], rmse_global)
                self.assertAlmostEqual(fila["r2_observaciones"], r2)
                self.assertNotAlmostEqual(rmse, rmse_global, places=3)
                self.assertEqual(round(mae, 3), publicados[(resultado["protocolo"], modelo)])

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

    def test_negativas_y_agua_sin_cambiar_el_ajuste(self):
        negativas = filas_con_prediccion_negativa(self.resultado_mapping["predicciones"], "mapping")
        self.assertEqual(int((negativas["modelo"] == "M1").sum()), 1)
        self.assertEqual(int((negativas["modelo"] == "M2").sum()), 22)
        self.assertTrue(negativas.loc[negativas["modelo"].eq("M2"), "en_el_extremo_de_la_curva"].all())
        self.assertTrue((~negativas["es_medicion"]).all())
        self.assertLess(float(negativas["prediccion_psi"].min()), -7.0)
        surging = filas_con_prediccion_negativa(self.resultado_surging["predicciones"], "surging")
        self.assertEqual(int((surging["modelo"] == "M1").sum()), 34)
        self.assertEqual(int((surging["modelo"] == "M2").sum()), 12)
        agua = self.resultado_mapping["fisico"]["agua"].set_index("curva_id")
        self.assertEqual(int(agua["subidas_medicion"].sum()), 0)
        self.assertEqual(int(agua["subidas_M1"].sum()), 0)
        self.assertGreater(int(agua.loc["50psig|3500|Single Phase", "subidas_M2"]), 0)
        self.assertLess(float(agua.loc["50psig|3500|Single Phase", "spearman_M2"]), 0.0)

    def test_la_columna_quitada_es_el_producto_estructural(self):
        marcada = marcar_pliegues(self.mapping, "mapping")
        entrena = marcada["pliegue"] != 0
        modelo = pipeline_m2("mapping", 0.1)
        modelo.fit(matriz_entradas(marcada.loc[entrena], "mapping"), marcada.loc[entrena, "dp2_3_psi"])
        nombres = modelo.named_steps["polinomio"].get_feature_names_out(
            modelo.named_steps["preparar"].nombres_salida_
        )
        soporte = modelo.named_steps["columnas_estructurales"].soporte_
        quitadas = [nombres[i] for i, queda in enumerate(soporte) if not queda]
        self.assertEqual(quitadas, ["es_monofasica qgd_tecnico"])
        self.assertIn("es_monofasica^2", list(nombres))
        self.assertEqual(int(self.mapping["qgd"].isna().sum()), 87)


class PruebasUnitariasSinteticas(unittest.TestCase):
    """No usan los CSV de la bomba. Sirven para el software, no como evidencia física."""

    def test_qgd_tecnico_en_una_matriz_inventada(self):
        marco = pd.DataFrame(
            {
                "condicion": ["Single Phase", "Qgd=0.01", "Qgd=0.01"],
                "ql_bpd": [100.0, 110.0, 120.0],
                "qgd": [np.nan, 0.01, 0.01],
                "velocidad_rpm": [1800, 1800, 1800],
                "psep_psig": [50.0, 50.0, 50.0],
            }
        )
        preparar = PrepararEntradas("mapping")
        preparar.fit(marco)
        salida = preparar.transform(marco)
        self.assertEqual(salida[0, 2], 0.0)
        self.assertTrue(np.isnan(marco.loc[0, "qgd"]))
        self.assertEqual(list(preparar.nombres_salida_), ["ql_bpd", "es_monofasica", "qgd_tecnico", "velocidad_rpm", "psep_psig"])

    def test_la_mascara_de_ceros_no_se_reajusta(self):
        entrenamiento = np.array([[0.0, 1.0], [0.0, 2.0], [0.0, 4.0]])
        paso = ColumnasEstructurales().fit(entrenamiento)
        self.assertEqual(list(paso.soporte_), [False, True])
        prueba = np.array([[5.0, 9.0], [6.0, 8.0]])
        transformada = paso.transform(prueba)
        self.assertEqual(transformada.shape, (2, 1))
        self.assertTrue(np.allclose(transformada[:, 0], [9.0, 8.0]))
        self.assertEqual(list(paso.soporte_), [False, True])

    def test_un_derivado_no_pisa_los_csv(self):
        with self.assertRaises(RuntimeError):
            guardar_derivado(pd.DataFrame({"a": [1]}), RAIZ / "data" / "processed" / "mapping_long.csv")



if __name__ == "__main__":
    unittest.main()
