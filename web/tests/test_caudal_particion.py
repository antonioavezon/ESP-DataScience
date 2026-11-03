"""Regresión: caudal de agua (RB-1521) y BOPD (RB-IA-2191) no se confunden con el total."""

from django.test import TestCase

from services.chat_intencion import interpretar
from services.chat_orquestador import responder
from services.ollama_client import Inferencia
from services.resultados_en_vivo import guardar


class _Modelo:
    def consultar(self, modelo, mensajes, num_predict):
        return Inferencia(
            ok=True,
            contenido='{"resumen":"ok","explicacion":"ok"}',
            error="",
            modelo=modelo,
            done_reason="stop",
        )

    def cerrar(self):
        return None


def _publicar_rb1521():
    guardar({
        "pozo_id": "RB-1521",
        "dataset_id": "RB-1521",
        "escenario_id": "base-RB-1521",
        "evaluacion_id": "base-RB-1521",
        "emitido_en": "2026-10-31T12:00:00+00:00",
        "modo": "escenario_inicial",
        "origen_valores": "hoja",
        "estado": {
            "codigo": "SIN_DATOS",
            "rotulo": "REGISTRO",
            "tono": "sin-clasificacion",
            "clasificacion_valida": False,
        },
        "texto": {"mensaje": "registro", "accion": "", "nota": "", "origen": "deterministico"},
        "resultados": {
            "q_fluidos": {"valor": 8977.0, "valor_visible": "8977", "unidad": "BFPD", "nombre": "Q-fluidos"},
            "bsw": {"valor": 0.985, "valor_visible": "0.985", "unidad": "fracción", "nombre": "BSW"},
            "q_water": {"valor": 8842.345, "valor_visible": "8842.34", "unidad": "BFPD", "nombre": "Q-water"},
            "q_oil": {"valor": 134.655, "valor_visible": "134.66", "unidad": "BFPD", "nombre": "Q-oil"},
        },
        "reglas_activas": [],
        "recomendacion_operacional_autorizada": False,
        "entradas": {},
    })


def _publicar_rbia():
    guardar({
        "pozo_id": "RB-IA-2191",
        "dataset_id": "RB-IA-2191",
        "escenario_id": "base-RB-IA-2191",
        "evaluacion_id": "base-RB-IA-2191",
        "emitido_en": "2026-10-31T12:00:00+00:00",
        "modo": "escenario_inicial",
        "origen_valores": "hoja",
        "estado": {
            "codigo": "SIN_DATOS",
            "rotulo": "REGISTRO",
            "tono": "sin-clasificacion",
            "clasificacion_valida": False,
        },
        "texto": {"mensaje": "registro", "accion": "", "nota": "", "origen": "deterministico"},
        "resultados": {
            "bfpd": {"valor": 5180.0, "valor_visible": "5180", "unidad": "BFPD", "nombre": "BFPD"},
            "bwpd": {"valor": 5099.4, "valor_visible": "5099.4", "unidad": "BFPD", "nombre": "BWPD"},
            "bopd": {"valor": 80.6, "valor_visible": "80.6", "unidad": "BFPD", "nombre": "BOPD"},
            "bsw": {"valor": 0.972, "valor_visible": "0.972", "unidad": "fracción", "nombre": "BSW"},
        },
        "reglas_activas": [],
        "recomendacion_operacional_autorizada": False,
        "entradas": {},
    })


class CaudalParticionTests(TestCase):
    def test_intencion_caudal_agua(self):
        decision = interpretar("¿Cuál es el caudal de agua?", pozo_formulario="RB-1521", ambito="pozo")
        self.assertEqual(decision["intencion"], "caudal")
        self.assertEqual(decision["variable"], "q_water")
        self.assertEqual(decision["pozos"], ["RB-1521"])

    def test_intencion_bopd(self):
        decision = interpretar("¿Cuál es el BOPD?", pozo_formulario="RB-IA-2191", ambito="pozo")
        self.assertEqual(decision["intencion"], "caudal")
        self.assertEqual(decision["variable"], "bopd")
        self.assertEqual(decision["pozos"], ["RB-IA-2191"])

    def test_respuesta_agua_no_usa_solo_total(self):
        _publicar_rb1521()
        salida = responder(
            "¿Cuál es el caudal de agua?",
            "RB-1521",
            {},
            _Modelo(),
            modelo="modelo-prueba",
            num_predict=64,
            dataset_id="RB-1521",
            ambito="pozo",
            alcance={"dataset": "RB-1521", "pozo": "RB-1521"},
        )
        inferencia = salida.get("inferencia") or {}
        texto = inferencia.get("contenido") or ""
        compacto = texto.replace(".", "").replace(",", "")
        self.assertIn("8842", compacto)
        self.assertIn("agua", texto.lower())
        self.assertNotIn("fuera de alcance", texto.lower())
        self.assertNotIn("fuera del tema", texto.lower())
        # El total puede aparecer, pero el agua no puede omitirse ni sustituirse solo por 8977.
        self.assertNotEqual(compacto.count("8977") > 0 and "8842" not in compacto, True)

    def test_respuesta_bopd_no_fuera_de_alcance(self):
        _publicar_rbia()
        salida = responder(
            "¿Cuál es el BOPD?",
            "RB-IA-2191",
            {},
            _Modelo(),
            modelo="modelo-prueba",
            num_predict=64,
            dataset_id="RB-IA-2191",
            ambito="pozo",
            alcance={"dataset": "RB-IA-2191", "pozo": "RB-IA-2191"},
        )
        inferencia = salida.get("inferencia") or {}
        texto = (inferencia.get("contenido") or "").lower()
        self.assertTrue(inferencia.get("ok"), inferencia)
        self.assertNotIn("fuera de alcance", texto)
        self.assertNotIn("no entra en ese tema", texto)
        self.assertTrue("80" in (inferencia.get("contenido") or "") or "bopd" in texto)
