"""Pruebas del servicio MODELOS IA: contrato HTTP/JSON y respaldo sin Ollama."""

from __future__ import annotations

import json
import sys
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "modelos_ia"))
sys.path.insert(0, str(RAIZ / "web"))

from servicio import Manejador, explicar_resultado  # noqa: E402


class ExplicarResultadoTests(unittest.TestCase):
    def test_documento_invalido_respaldo(self):
        salida = explicar_resultado([])  # type: ignore[arg-type]
        self.assertEqual(salida["estado_generacion"], "respaldo")
        self.assertTrue(salida["explicacion"])
        self.assertEqual(salida["modelo"], "")

    def test_resultado_deterministico_sin_ollama(self):
        documento = {
            "evaluacion_id": "ev-prueba",
            "pozo_id": "QF-084",
            "estado": {
                "codigo": "NORMAL",
                "rotulo": "NORMAL",
                "tono": "normal",
                "clasificacion_valida": True,
                "fundamento": "RC-BES-03",
            },
            "texto": {
                "mensaje": "El caudal está entre el mínimo y el máximo escritos a esta frecuencia.",
                "accion": "",
                "origen": "deterministico",
            },
            "modificadas": [],
            "entradas": {"frecuencia_hz": {"valor": 63.0, "unidad": "Hz"}},
            "resultados": {"pip_ft": {"valor": 1714.5, "unidad": "ft"}},
        }
        with patch("services.mensajes_operador.ClienteOllama") as cliente:
            cliente.side_effect = RuntimeError("ollama ausente en prueba")
            salida = explicar_resultado(documento)
        self.assertEqual(salida["pozo_id"], "QF-084")
        self.assertEqual(salida["evaluacion_id"], "ev-prueba")
        self.assertIn(salida["estado_generacion"], ("respaldo", "generada"))
        self.assertIsInstance(salida["explicacion"], str)
        self.assertIsInstance(salida["advertencias"], list)


class HttpContratoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from http.server import ThreadingHTTPServer

        cls.servidor = ThreadingHTTPServer(("127.0.0.1", 0), Manejador)
        cls.puerto = cls.servidor.server_address[1]
        cls.hilo = threading.Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.hilo.start()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()

    def test_salud(self):
        conn = HTTPConnection("127.0.0.1", self.puerto, timeout=5)
        conn.request("GET", "/salud")
        resp = conn.getresponse()
        cuerpo = json.loads(resp.read().decode("utf-8"))
        conn.close()
        self.assertEqual(resp.status, 200)
        self.assertTrue(cuerpo.get("disponible"))

    def test_explicar_json(self):
        documento = {
            "evaluacion_id": "ev-http",
            "pozo_id": "RB-1521",
            "estado": {"codigo": "SIN_DATOS", "rotulo": "REGISTRO", "clasificacion_valida": False},
            "texto": {"mensaje": "registro", "accion": "", "origen": "deterministico"},
            "resultados": {"q_water": {"valor": 8842.345, "unidad": "BFPD"}},
        }
        carga = json.dumps(documento).encode("utf-8")

        class _FakeInferencia:
            ok = True
            contenido = "Explicación de prueba."
            error = ""
            modelo = "modelo-prueba"
            done_reason = "stop"
            incompleta = False

        class _FakeCliente:
            def __init__(self, *a, **k):
                pass

            def consultar(self, *a, **k):
                return _FakeInferencia()

            def cerrar(self):
                return None

        with patch("services.mensajes_operador.ClienteOllama", _FakeCliente):
            conn = HTTPConnection("127.0.0.1", self.puerto, timeout=5)
            conn.request(
                "POST",
                "/v1/explicar",
                body=carga,
                headers={"Content-Type": "application/json", "Content-Length": str(len(carga))},
            )
            resp = conn.getresponse()
            cuerpo = json.loads(resp.read().decode("utf-8"))
            conn.close()
        self.assertEqual(resp.status, 200)
        for clave in ("explicacion", "accion", "evaluacion_id", "pozo_id", "modelo", "estado_generacion", "advertencias"):
            self.assertIn(clave, cuerpo)
        self.assertEqual(cuerpo["pozo_id"], "RB-1521")

    def test_json_invalido_400(self):
        conn = HTTPConnection("127.0.0.1", self.puerto, timeout=5)
        conn.request(
            "POST",
            "/v1/explicar",
            body=b"{no-json",
            headers={"Content-Type": "application/json", "Content-Length": "8"},
        )
        resp = conn.getresponse()
        cuerpo = json.loads(resp.read().decode("utf-8"))
        conn.close()
        self.assertEqual(resp.status, 400)
        self.assertEqual(cuerpo["estado_generacion"], "respaldo")


if __name__ == "__main__":
    unittest.main()
