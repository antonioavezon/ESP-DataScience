"""Regresión B.3: PIP se define como Pump Intake Pressure, no como otra magnitud."""

from django.test import TestCase

from services.chat_intencion import interpretar
from services.technical_context import DEFINICION_PIP, construir


class PipDefinicionTests(TestCase):
    def test_definicion_es_presion_de_admision(self):
        texto = DEFINICION_PIP.lower()
        self.assertIn("pump intake pressure", texto)
        self.assertIn("entrada", texto)
        self.assertIn("no significa", texto)
        self.assertIn("inicio de producción", texto)
        self.assertIn("impulsión", texto)

    def test_intencion_conceptual_pip(self):
        decision = interpretar("¿Qué es el PIP?")
        self.assertEqual(decision["intencion"], "conceptual")

    def test_contexto_incluye_definicion(self):
        ctx = construir(None, None)
        bloques = " ".join(b["texto"] for b in ctx["bloques"]).lower()
        self.assertIn("pump intake pressure", bloques)
        self.assertIn("entrada", bloques)
