"""Pozo o dataset citados en el texto deben mandar aunque el selector diga Todos."""

from unittest.mock import patch

from django.test import TestCase

from services.chat_intencion import interpretar
from services.chat_orquestador import responder
from services.ollama_client import Inferencia


class _Modelo:
    def __init__(self, *args, **kwargs):
        pass

    def consultar(self, *args, **kwargs):
        return Inferencia(
            ok=True,
            contenido='{"resumen":"Resumen.","explicacion":"Detalle."}',
            modelo="modelo-prueba",
            done_reason="stop",
        )

    def cerrar(self):
        return None


class PozoEnPreguntaTests(TestCase):
    def test_rb1521_en_texto_sin_selector(self):
        decision = interpretar(
            'El pozo RB-1521 está en estado "registro", por qué?',
            {},
            None,
            "dataset",
        )
        self.assertEqual(decision["intencion"], "estado")
        self.assertEqual(decision["pozos"], ["RB-1521"])
        self.assertIn("RB-1521", decision.get("datasets") or [])

    def test_qf084_en_texto_sin_selector(self):
        decision = interpretar("¿Cómo está QF-084?", {}, None, "dataset")
        self.assertEqual(decision["intencion"], "estado")
        self.assertEqual(decision["pozos"], ["QF-084"])

    def test_dataset_bes_jun_en_texto(self):
        decision = interpretar("¿Cómo están los pozos de BES-jun?", {}, None, "dataset")
        self.assertEqual(decision["intencion"], "estado")
        self.assertEqual(decision.get("datasets"), ["BES-jun"])

    def test_presion_con_pozo_en_texto(self):
        decision = interpretar("¿Qué presión tiene QF-301?", {}, None, "dataset")
        self.assertEqual(decision["intencion"], "presiones")
        self.assertEqual(decision["pozos"], ["QF-301"])

    def test_orquestador_usa_pozo_del_texto(self):
        salida = responder(
            "¿Cómo está QF-084?",
            None,
            {},
            _Modelo(),
            modelo="modelo-prueba",
            num_predict=64,
            dataset_id="ALL",
            ambito="dataset",
            alcance={"dataset": "Todos", "pozo": "Todos"},
        )
        inf = salida["inferencia"]
        self.assertTrue(inf["ok"])
        self.assertEqual(inf["alcance"]["pozo"], "QF-084")
        self.assertEqual(inf["alcance"]["dataset"], "BES-jun")
        self.assertIn("QF-084", inf["contenido"])
        self.assertIn("NORMAL", inf["contenido"])
        self.assertNotIn("Inventario de pozos", inf["contenido"])

    def test_orquestador_bes_jun_en_texto(self):
        salida = responder(
            "¿Cómo están los pozos de BES-jun?",
            None,
            {},
            _Modelo(),
            modelo="modelo-prueba",
            num_predict=64,
            dataset_id="ALL",
            ambito="dataset",
            alcance={"dataset": "Todos", "pozo": "Todos"},
        )
        inf = salida["inferencia"]
        self.assertTrue(inf["ok"])
        self.assertEqual(inf["alcance"]["dataset"], "BES-jun")
        self.assertIn("QF-084", inf["contenido"])
        self.assertNotIn("Inventario de pozos", inf["contenido"])

    def test_vista_pregunta_con_pozo_sin_selector(self):
        with patch("apps.asistente_ia.views.ClienteOllama", _Modelo):
            respuesta = self.client.post("/asistente/enviar/", {
                "consulta": "¿Cómo está QF-084?",
                "dataset_id": "ALL",
                "pozo_id": "",
            }, follow=True)
        self.assertContains(respuesta, "QF-084")
        self.assertContains(respuesta, "NORMAL")
        self.assertNotContains(respuesta, "Inventario de pozos")
