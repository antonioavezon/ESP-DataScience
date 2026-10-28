"""Fronteras de PROCESO y DATA. No arranca Django."""

import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "web"))

EXCEL = RAIZ / "datasets" / "en_uso" / "BES-jun" / "entrada" / "BES_jun.xlsx"
HASH = "ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85"


class Formulas(unittest.TestCase):
    def test_lista_sin_calcular(self):
        comando = [sys.executable, str(RAIZ / "proceso" / "formulas.py"), "list"]
        resultado = subprocess.run(comando, cwd=RAIZ, capture_output=True, text=True, check=False)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("E-01", resultado.stdout)
        self.assertIn("141.5 / (131.5 + API)", resultado.stdout)
        self.assertIn("M-BES-FLUIDO", resultado.stdout)
        self.assertNotIn("pendiente de validación", resultado.stdout.casefold())
        self.assertEqual(hashlib.sha256(EXCEL.read_bytes()).hexdigest(), HASH)


class Escenarios(unittest.TestCase):
    def test_cinco_pozos_y_rechazo(self):
        from data.simuladores.escenarios import base, pozos, validar

        identificadores = [item["pozo_id"] for item in pozos() if item["evaluable"]]
        self.assertEqual(identificadores, ["QF-084", "QF-301", "QF-147", "QF-005", "QF-306", "RB-1521"])
        serie = base("RB-1521")
        self.assertEqual([item["id"] for item in serie["controles"]], ["caudal_fluidos", "bsw"])
        _, ajeno = validar("RB-1521", {"frecuencia_hz": 60})
        self.assertIn("no es una entrada", ajeno)
        ficha = base("QF-084")
        self.assertEqual([item["id"] for item in ficha["controles"]], ["frecuencia_hz", "caudal_operacion_bfpd"])
        cambios, error = validar("QF-084", {"frecuencia_hz": 60})
        self.assertIsNone(error)
        self.assertEqual(cambios, {"frecuencia_hz": 60.0})
        _, rechazo = validar("QF-084", {"tvd_intake_ft": 2700})
        self.assertIn("no es una entrada", rechazo)
        _, fuera = validar("QF-084", {"frecuencia_hz": 10})
        self.assertIn("fuera del recorrido", fuera)
        otro = base("QF-301")
        self.assertNotEqual(otro["controles"][0]["valor_original"], ficha["controles"][0]["valor_original"])
        self.assertEqual(hashlib.sha256(EXCEL.read_bytes()).hexdigest(), HASH)


if __name__ == "__main__":
    unittest.main()
