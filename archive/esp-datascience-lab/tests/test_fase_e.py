"""Fase E: papeles de referencia. No reajusta modelos.

Los cuadros de esta clase no son datos de la bomba.
"""

import os
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from esp_datascience.fase_e import papeles, resumen_de_m5
from esp_datascience.protocolo import VERSION
from esp_datascience.rutas import huella_sha256

ARCHIVOS = {
    "data/raw/mapping.xlsx": "3b933ca84911484f5d912a44b025f5589abaf5ebc2b0426bf80c083869762bda",
    "data/raw/surging.xlsx": "acdcc6c5fc3d8969280c8712c45657fbb863f163a60829584fece5abf75f28cd",
    "data/processed/mapping_long.csv": "ff68e36703d3d3901b8bd964008c49b062afa9d89a817b9d66e7849f9b400648",
    "data/processed/surging_long.csv": "f58e8e2cac74acdf2081479ec8769422f39c4e4665f5b3ff472df4a70b15bd96",
}


class SinteticosDeLaFaseE(unittest.TestCase):
    def test_el_menor_mae_no_nombra_un_ganador_unico(self):
        salida = papeles(
            {
                "mapping": {"M1": 4.0, "M2": 2.0, "M3": 3.5, "M4": 1.0},
                "surging": {"M1": 3.0, "M2": 1.5, "M3": 2.5, "M4": 0.8},
            }
        )
        self.assertEqual(salida["candidato_de_precision"], "M4")
        self.assertEqual(salida["referencia_interpretable"], "M1")
        self.assertEqual(salida["referencia_no_lineal"], "M2")
        self.assertIsNone(salida["ganador_unico"])
        self.assertNotIn("M5", salida["mejor_precision_por_protocolo"]["mapping"])

    def test_protocolos_distintos_no_fuerzan_un_preciso(self):
        salida = papeles(
            {
                "mapping": {"M1": 1.0, "M2": 2.0, "M3": 3.0, "M4": 4.0},
                "surging": {"M1": 4.0, "M2": 3.0, "M3": 2.0, "M4": 1.0},
            }
        )
        self.assertIsNone(salida["candidato_de_precision"])
        self.assertEqual(salida["mejor_precision_por_protocolo"]["mapping"], "M1")
        self.assertEqual(salida["mejor_precision_por_protocolo"]["surging"], "M4")
        self.assertEqual(salida["referencia_interpretable"], "M1")

    def test_m5_no_entra_en_la_tabla_global_ni_en_las_treinta_curvas(self):
        with self.assertRaises(ValueError):
            papeles({"mapping": {"M1": 1.0, "M2": 1.0, "M3": 1.0, "M4": 1.0, "M5": 2.0}})
        parcial = resumen_de_m5({"M1": 3.0, "M2": 1.0, "M5": 2.0}, n_curvas=5, n_curvas_del_protocolo=30)
        self.assertTrue(parcial["cobertura_parcial"])
        self.assertEqual(parcial["n_curvas"], 5)
        self.assertAlmostEqual(parcial["mae_m5_psi"], 2.0)
        with self.assertRaises(ValueError):
            resumen_de_m5({"M5": 2.0}, n_curvas=30, n_curvas_del_protocolo=30)


class IntegridadSinReajustar(unittest.TestCase):
    def test_el_protocolo_y_los_archivos_siguen_igual(self):
        os.chdir(RAIZ)
        self.assertEqual(VERSION, "2.14-A")
        for relativo, esperada in ARCHIVOS.items():
            self.assertEqual(huella_sha256(RAIZ / relativo), esperada)


if __name__ == "__main__":
    unittest.main()
