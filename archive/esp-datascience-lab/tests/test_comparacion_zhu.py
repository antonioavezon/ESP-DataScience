"""Pruebas de la guarda de comparación de la actividad 2.15."""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from esp_datascience.comparacion_zhu import (
    CONDICIONES_NUMERICAS,
    PARES_NO_EQUIVALENTES,
    RegistroCondicion,
    ResultadoPuerta,
    auditar_matriz,
    dossier_de_la_actividad_215,
    exigir_comparacion_numerica,
)
from esp_datascience.entrenamiento import HUELLAS_PLIEGUES
from esp_datascience.particiones import SEMILLA
from esp_datascience.protocolo import VERSION
from esp_datascience.rutas import huella_sha256


def _registros_citados(resultado="cumple"):
    return [
        RegistroCondicion(
            condicion=nombre,
            resultado=resultado,
            fuente="fuente de prueba, no es la bomba",
            observaciones="registro sintético",
            estado="citada_en_fuente",
        )
        for nombre in CONDICIONES_NUMERICAS
    ]


class Guardas(unittest.TestCase):
    def test_qgd_no_equivale_a_gvf(self):
        pares = {(a, b) for a, b, _ in PARES_NO_EQUIVALENTES}
        self.assertIn(("qgd", "gvf0_porcentaje"), pares)
        self.assertIn(("dp2_3_psi", "presion_absoluta"), pares)

    def test_un_booleano_no_abre_la_puerta(self):
        with self.assertRaises(TypeError):
            exigir_comparacion_numerica(True)
        with self.assertRaises(TypeError):
            exigir_comparacion_numerica([True] * len(CONDICIONES_NUMERICAS))

    def test_la_puerta_abierta_no_declara_equivalencia_fisica(self):
        salida = exigir_comparacion_numerica(_registros_citados())
        self.assertTrue(salida.puerta_administrativa)
        self.assertFalse(salida.equivalencia_fisica_demostrada)
        with self.assertRaises(ValueError):
            ResultadoPuerta(True, True, "no debe aceptarse")

    def test_el_dossier_de_215_mantiene_la_puerta_cerrada(self):
        with self.assertRaises(ValueError):
            exigir_comparacion_numerica(dossier_de_la_actividad_215())

    def test_una_cita_sin_fuente_no_se_construye(self):
        with self.assertRaises(ValueError):
            RegistroCondicion(
                "objetivo_comun",
                "cumple",
                "  ",
                "sin documento",
                "citada_en_fuente",
            )

    def test_la_matriz_no_tiene_huecos_ni_duplicados(self):
        resumen = auditar_matriz(RAIZ / "docs/matriz_evidencias_2_15.csv")
        self.assertGreaterEqual(resumen["filas"], 19)
        self.assertEqual(len(resumen["identificadores"]), len(set(resumen["identificadores"])))
        texto = (RAIZ / "docs/matriz_evidencias_2_15.csv").read_text(encoding="utf-8")
        self.assertNotIn("páginas 20-80", texto)
        self.assertIn("página impresa 45", texto)
        self.assertIn("ecuación (2.7)", texto)

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
