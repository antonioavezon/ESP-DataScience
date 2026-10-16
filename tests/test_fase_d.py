"""Fase D: comparación e incertidumbre. No reajusta modelos ni cambia 2.14-A.

Los cuadros de esta clase sintética no son datos de la bomba.
"""

import os
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from esp_datascience.entrenamiento import evaluar_protocolo
from esp_datascience.fase_d import (
    N_REPLICAS,
    SEMILLA_BOOTSTRAP,
    bonferroni_posterior,
    bootstrap_conglomerados,
    bootstrap_media,
    delta_mae,
    detalle_de_ponderacion,
    diagnostico_sin_un_conglomerado,
    mae_por_curva,
    monotonía_de_agua,
    notas_de_agua_bajo_umbrales,
    origen_de_velocidad,
    pesos_efectivos,
    primeros_por_ponderacion,
    puntuacion_de_agua,
    puntuacion_por_spearman,
    puntuacion_por_subidas_de_gas,
    resumen_delta,
    resumen_negativas,
)
from esp_datascience.particiones import SEMILLA
from esp_datascience.protocolo import VERSION, huella_pliegues
from esp_datascience.rutas import huella_sha256

HUELLAS = {
    "mapping": "f35be865a01a6255cc08afdccb96863184ad394a550d9a5249d42b4041a8d948",
    "surging": "71c4818c4b3a5bce0d363c5df658e04141ce1c1301e72f754d5805a52c9dc742",
}
ARCHIVOS = {
    "data/raw/mapping.xlsx": "3b933ca84911484f5d912a44b025f5589abaf5ebc2b0426bf80c083869762bda",
    "data/raw/surging.xlsx": "acdcc6c5fc3d8969280c8712c45657fbb863f163a60829584fece5abf75f28cd",
    "data/processed/mapping_long.csv": "ff68e36703d3d3901b8bd964008c49b062afa9d89a817b9d66e7849f9b400648",
    "data/processed/surging_long.csv": "f58e8e2cac74acdf2081479ec8769422f39c4e4665f5b3ff472df4a70b15bd96",
}


def _serie(valores, indice):
    return pd.Series(valores, index=indice, dtype=float)


class SinteticosDeLaFaseD(unittest.TestCase):
    def test_el_bootstrap_remuestrea_curvas_y_se_repite(self):
        delta = _serie([-2.0, 1.0, -1.0, -1.0], ["c1", "c2", "c3", "c4"])
        primera = bootstrap_media(delta, n_replicas=2000, semilla=214)
        segunda = bootstrap_media(delta, n_replicas=2000, semilla=214)
        self.assertEqual(primera["n_curvas"], 4)
        self.assertEqual(primera["unidad"], "curva")
        self.assertEqual(primera["intervalo_inferior_psi"], segunda["intervalo_inferior_psi"])
        self.assertEqual(primera["intervalo_superior_psi"], segunda["intervalo_superior_psi"])
        self.assertLess(primera["intervalo_inferior_psi"], primera["media_psi"])
        self.assertGreater(primera["intervalo_superior_psi"], primera["media_psi"])
        constante = bootstrap_media(_serie([2.0, 2.0, 2.0], ["a", "b", "c"]), n_replicas=1000, semilla=1)
        self.assertAlmostEqual(constante["intervalo_inferior_psi"], 2.0)
        self.assertAlmostEqual(constante["intervalo_superior_psi"], 2.0)

    def test_un_indice_repetido_no_entra_al_remuestreo(self):
        repetida = pd.Series([1.0, 2.0], index=["misma", "misma"])
        with self.assertRaises(ValueError):
            bootstrap_media(repetida, n_replicas=1000, semilla=1)
        with self.assertRaises(ValueError):
            bootstrap_media(_serie([1.0, np.nan], ["a", "b"]), n_replicas=1000, semilla=1)

    def test_el_conglomerado_no_parte_una_curva(self):
        delta = _serie([1.0, 3.0, 10.0], ["a", "b", "c"])
        grupo = pd.Series(["g1", "g1", "g2"], index=delta.index)
        salida = bootstrap_conglomerados(delta, grupo, n_replicas=1000, semilla=7)
        self.assertEqual(salida["n_conglomerados"], 2)
        self.assertEqual(salida["n_curvas"], 3)
        self.assertEqual(salida["unidad"], "conglomerado de curvas")

    def test_la_comparacion_pareada_exige_las_mismas_curvas(self):
        referencia = _serie([1.0, 2.0, 3.0], ["a", "b", "c"])
        candidata = _serie([0.0, 2.5], ["a", "b"])
        with self.assertRaises(ValueError):
            delta_mae(referencia, candidata, exigir_las_mismas=True)
        comun = delta_mae(referencia, candidata, exigir_las_mismas=False)
        self.assertEqual(list(comun.index), ["a", "b"])
        self.assertAlmostEqual(float(comun.loc["a"]), -1.0)
        cifras = resumen_delta(comun)
        self.assertEqual(cifras["curvas_que_mejoran"], 1)
        self.assertEqual(cifras["curvas_que_empeoran"], 1)

    def test_negativas_y_monotonia_en_un_cuadro_inventado(self):
        pred = pd.DataFrame(
            {
                "curva_id": ["agua", "agua", "agua", "gas", "gas"],
                "abscisa": [1.0, 2.0, 3.0, 1.0, 2.0],
                "condicion": ["Single Phase", "Single Phase", "Single Phase", "Qgd=0.01", "Qgd=0.01"],
                "medicion": [5.0, 4.0, 3.0, 2.0, 1.0],
                "prediccion_m1": [5.0, 4.0, 3.0, 2.0, -0.2],
                "prediccion_m4": [5.0, 6.0, 2.0, 2.0, 1.0],
            }
        )
        negativas = resumen_negativas(pred, "prediccion_m1", "M1")
        self.assertEqual(negativas["n_predicciones"], 1)
        self.assertEqual(negativas["n_curvas"], 1)
        agua = monotonía_de_agua(pred, {"M1": "prediccion_m1", "M4": "prediccion_m4"})
        fila = agua.set_index("curva_id").loc["agua"]
        self.assertEqual(int(fila["subidas_medicion"]), 0)
        self.assertEqual(int(fila["subidas_M1"]), 0)
        self.assertEqual(int(fila["subidas_M4"]), 1)
        self.assertAlmostEqual(float(fila["mayor_subida_M4"]), 1.0)

    def test_los_pesos_pueden_cambiar_el_primero(self):
        notas = pd.DataFrame(
            {
                "precision": [0, 3],
                "robustez": [1, 3],
                "agua": [3, 0],
                "negativas": [3, 3],
                "gas": [3, 1],
                "lectura": [3, 0],
                "simplicidad": [3, 0],
            },
            index=["lineal", "flexible"],
        )
        orden = primeros_por_ponderacion(notas)
        primeros = set(orden["primero"])
        self.assertGreater(len(primeros), 1)

    def test_los_cortes_de_gas_son_los_declarados(self):
        self.assertEqual(puntuacion_por_subidas_de_gas(0), 3)
        self.assertEqual(puntuacion_por_subidas_de_gas(1), 2)
        self.assertEqual(puntuacion_por_subidas_de_gas(4), 0)
        self.assertEqual(puntuacion_por_subidas_de_gas(1, modo="binario"), 0)
        self.assertEqual(puntuacion_por_spearman(-1.0), 3)
        self.assertEqual(puntuacion_por_spearman(-0.97), 2)
        self.assertEqual(puntuacion_por_spearman(-0.97, cortes=(-0.999, -0.99, -0.95)), 1)

    def test_retirar_un_conglomerado_no_parte_curvas(self):
        delta = _serie([1.0, 3.0, 10.0], ["a", "b", "c"])
        grupo = pd.Series(["g1", "g1", "g2"], index=delta.index)
        salida = diagnostico_sin_un_conglomerado(delta, grupo).set_index("conglomerado_retirado")
        self.assertEqual(int(salida.loc["g1", "n_curvas_retiradas"]), 2)
        self.assertEqual(int(salida.loc["g1", "n_curvas_restantes"]), 1)
        self.assertAlmostEqual(float(salida.loc["g1", "media_restante_psi"]), 10.0)
        self.assertIn("posterior", salida.loc["g1", "caracter"])
        aviso = bootstrap_conglomerados(delta, grupo, n_replicas=1000, semilla=7)
        self.assertTrue(aviso["base_limitada"])

    def test_un_umbral_posterior_cambia_la_nota_sin_cambiar_el_paso(self):
        agua = pd.DataFrame(
            {
                "subidas_M2": [2],
                "mayor_subida_M2": [5.5],
                "subidas_M4": [4],
                "mayor_subida_M4": [11.0],
            }
        )
        self.assertEqual(puntuacion_de_agua(agua, "M2"), 1)
        self.assertEqual(puntuacion_de_agua(agua, "M4"), 0)
        notas = notas_de_agua_bajo_umbrales(agua).set_index(["escenario", "modelo"])
        self.assertEqual(int(notas.loc[("mas_estricto", "M2"), "nota"]), 0)
        self.assertEqual(int(notas.loc[("mas_holgado", "M4"), "nota"]), 1)
        self.assertEqual(int(notas.loc[("publicado", "M4"), "nota"]), 0)
        self.assertTrue(notas["caracter"].str.contains("posterior").all())

    def test_un_criterio_ausente_se_omite_y_reescala(self):
        notas = pd.DataFrame({"precision": [0.0, 3.0], "agua": [3.0, 0.0]}, index=["legible", "flexible"])
        info = pesos_efectivos({"precision": 1, "agua": 3, "gas": 9}, notas.columns)
        self.assertEqual(info["omitidos"], ["gas"])
        self.assertAlmostEqual(info["pesos_renormalizados"]["precision"], 0.25)
        self.assertAlmostEqual(info["pesos_renormalizados"]["agua"], 0.75)
        self.assertTrue(info["renormaliza"])
        detalle = detalle_de_ponderacion(notas)
        self.assertTrue(detalle["criterios_omitidos"].str.contains("gas").all())
        self.assertFalse(detalle["criterios_omitidos"].str.contains("agua").any())
        self.assertGreater(detalle["ponderacion"].nunique(), 1)

    def test_bonferroni_no_sustituye_el_original_y_no_pasa_de_uno(self):
        originales = [0.01, 0.2]
        ajustados = bonferroni_posterior(originales)
        self.assertEqual(originales, [0.01, 0.2])
        self.assertAlmostEqual(ajustados[0], 0.02)
        self.assertAlmostEqual(ajustados[1], 0.4)
        self.assertEqual(bonferroni_posterior([0.6, 0.6]), [1.0, 1.0])


class IntegridadSinReajustar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.chdir(RAIZ)
        cls.mapping = pd.read_csv(RAIZ / "data/processed/mapping_long.csv")
        cls.surging = pd.read_csv(RAIZ / "data/processed/surging_long.csv")

    def test_huellas_y_origen_confundido_con_la_presion(self):
        self.assertEqual(VERSION, "2.14-A")
        self.assertEqual(SEMILLA_BOOTSTRAP, SEMILLA)
        self.assertEqual(N_REPLICAS, 10_000)
        self.assertEqual(huella_pliegues(self.mapping, "mapping"), HUELLAS["mapping"])
        self.assertEqual(huella_pliegues(self.surging, "surging"), HUELLAS["surging"])
        for relativo, esperada in ARCHIVOS.items():
            self.assertEqual(huella_sha256(RAIZ / relativo), esperada)
        origen = origen_de_velocidad(self.mapping)
        self.assertEqual(set(origen.loc[origen["psep_psig"].eq(50), "origen_velocidad"]), {"celda"})
        self.assertEqual(set(origen.loc[origen["psep_psig"].gt(50), "origen_velocidad"]), {"diseño_experimental"})
        for relativo, esperada in ARCHIVOS.items():
            self.assertEqual(huella_sha256(RAIZ / relativo), esperada)

    def test_m1_y_m2_siguen_en_las_cifras_publicadas(self):
        resultado = evaluar_protocolo(self.mapping, "mapping")
        pred = resultado["predicciones"]
        mae = mae_por_curva(pred, "prediccion_m1")
        self.assertEqual(round(float(mae.mean()), 3), 3.999)
        self.assertEqual(round(float(mae_por_curva(pred, "prediccion_m2").mean()), 3), 1.364)
        self.assertEqual(len(mae), 30)


if __name__ == "__main__":
    unittest.main()
