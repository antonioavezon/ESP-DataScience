"""Regresión: BOPD/BWPD/BFPD no se etiquetan indistintamente."""

from django.test import TestCase

from services.chat_intencion import interpretar
from services.chat_orquestador import responder
from services.ollama_client import Inferencia
from services.resultados_en_vivo import guardar
from services.unidades_caudal import unidad_de


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


class UnidadesCaudalTests(TestCase):
    def test_canonicas(self):
        self.assertEqual(unidad_de("bopd", "BFPD"), "BOPD")
        self.assertEqual(unidad_de("bwpd", "BFPD"), "BWPD")
        self.assertEqual(unidad_de("bfpd", "BFPD"), "BFPD")
        self.assertEqual(unidad_de("q_water", "BFPD"), "BWPD")
        self.assertEqual(unidad_de("q_oil", "BFPD"), "BOPD")

    def test_definicion_bopd(self):
        decision = interpretar("¿Qué significa BOPD?")
        self.assertEqual(decision["intencion"], "conceptual")
        self.assertEqual(decision["variable"], "bopd")

    def test_definicion_pip_sin_que(self):
        for consulta in ("¿PIP es presión de impulsión?", "explica la PIP"):
            decision = interpretar(consulta)
            self.assertEqual(decision["intencion"], "conceptual", consulta)
            self.assertEqual(decision["variable"], "pip", consulta)

    def test_diferencia_presion_altura_es_conceptual(self):
        for consulta in (
            "diferencia entre presión y altura hidráulica",
            "¿Cuál es la diferencia entre presión y altura hidráulica?",
            "distingue presión frente a altura hidráulica",
        ):
            decision = interpretar(consulta)
            self.assertEqual(decision["intencion"], "conceptual", consulta)
            self.assertEqual(decision["variable"], "presion_altura", consulta)

    def test_petroleo_produce_intencion(self):
        decision = interpretar("¿Cuánto petróleo produce?", pozo_formulario="RB-IA-2191", ambito="pozo")
        self.assertEqual(decision["intencion"], "caudal")
        self.assertEqual(decision["variable"], "bopd")

    def test_respuesta_bopd_usa_unidad_bopd(self):
        # Publica deliberadamente unidad incorrecta BFPD para comprobar normalización.
        guardar({
            "pozo_id": "RB-IA-2191",
            "dataset_id": "RB-IA-2191",
            "escenario_id": "base-RB-IA-2191",
            "evaluacion_id": "base-RB-IA-2191",
            "emitido_en": "2026-10-31T15:00:00+00:00",
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
            },
            "reglas_activas": [],
            "recomendacion_operacional_autorizada": False,
            "entradas": {},
        })
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
        texto = (salida.get("inferencia") or {}).get("contenido") or ""
        self.assertIn("80", texto)
        self.assertRegex(texto, r"80[,.]?6\s*BOPD")
        # El petróleo no debe etiquetarse como BFPD en la celda BOPD.
        self.assertNotRegex(texto, r"80[,.]?6\s*BFPD")
