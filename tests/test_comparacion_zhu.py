"""Pruebas de la guarda de comparación de la actividad 2.15."""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from esp_datascience.comparacion_zhu import (
    CONDICIONES_NUMERICAS,
    PARES_NO_EQUIVALENTES,
    exigir_comparacion_numerica,
)
from esp_datascience.entrenamiento import HUELLAS_PLIEGUES
from esp_datascience.particiones import SEMILLA
from esp_datascience.protocolo import VERSION
from esp_datascience.rutas import huella_sha256


class Guardas(unittest.TestCase):
    def test_qgd_no_equivale_a_gvf(self):
        pares = {(a, b) for a, b, _ in PARES_NO_EQUIVALENTES}
        self.assertIn(("qgd", "gvf0_porcentaje"), pares)
        self.assertIn(("dp2_3_psi", "presion_absoluta"), pares)

    def test_rechaza_si_falta_una_condicion(self):
        completo = {nombre: True for nombre in CONDICIONES_NUMERICAS}
        exigir_comparacion_numerica(**completo)
        incompleto = dict(completo)
        incompleto["ecuacion_verificada"] = False
        with self.assertRaises(ValueError):
            exigir_comparacion_numerica(**incompleto)

    def test_las_huellas_de_214_siguen_iguales(self):
        self.assertEqual(VERSION, "2.14-A")
        self.assertEqual(SEMILLA, 214)
        self.assertEqual(
            HUELLAS_PLIEGUES["mapping"],
            "f35be865a01a6255cc08afdccb96863184ad394a550d9a5249d42b4041a8d948",
        )
        self.assertEqual(
            HUELLAS_PLIEGUES["surging"],
            "71c4818c4b3a5bce0d363c5df658e04141ce1c1301e72f754d5805a52c9dc742",
        )
        esperadas = {
            "data/raw/mapping.xlsx": "3b933ca84911484f5d912a44b025f5589abaf5ebc2b0426bf80c083869762bda",
            "data/raw/surging.xlsx": "acdcc6c5fc3d8969280c8712c45657fbb863f163a60829584fece5abf75f28cd",
            "data/processed/mapping_long.csv": "ff68e36703d3d3901b8bd964008c49b062afa9d89a817b9d66e7849f9b400648",
            "data/processed/surging_long.csv": "f58e8e2cac74acdf2081479ec8769422f39c4e4665f5b3ff472df4a70b15bd96",
        }
        for relativo, huella in esperadas.items():
            self.assertEqual(huella_sha256(RAIZ / relativo), huella)


if __name__ == "__main__":
    unittest.main()
