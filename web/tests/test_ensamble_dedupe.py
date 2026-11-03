"""Regresión: el ensamble no repite la misma frase ni inventa cifras."""

from django.test import TestCase

from services.chat_contrato import fusionar_linguistica, texto_plano
from services.chat_dedupe import aporta_novedad, dedupe_frases
from services.chat_intencion import interpretar
from services.chat_orquestador import responder
from services.ollama_client import Inferencia
from services.resultados_en_vivo import guardar


class _Modelo:
    def __init__(self, contenido):
        self.contenido = contenido

    def consultar(self, *a, **k):
        return Inferencia(
            ok=True, contenido=self.contenido, error="", modelo="m", done_reason="stop",
        )

    def cerrar(self):
        return None


class DedupeTests(TestCase):
    def test_dedupe_frases(self):
        texto = (
            "El BOPD es 80,6 BOPD. "
            "El BOPD es 80,6 BOPD. "
            "La unidad es BOPD."
        )
        limpio = dedupe_frases(texto)
        self.assertEqual(limpio.count("80,6"), 1)

    def test_fusion_no_repite_resumen(self):
        contrato = {
            "schema_version": "1.0",
            "response_id": "t1",
            "context": {"dataset_id": "RB-IA-2191", "well_id": "RB-IA-2191", "scenario_id": None},
            "answer": {
                "type": "flow",
                "title": "BOPD",
                "summary": "BOPD publicado.",
                "blocks": [
                    {
                        "type": "table",
                        "heading": "Caudales",
                        "columns": ["Pozo", "BOPD"],
                        "rows": [["RB-IA-2191", "80,6 BOPD"]],
                    },
                    {
                        "type": "paragraph",
                        "text": "BOPD es el caudal de petróleo del resultado; no se inventa a partir de otra magnitud.",
                    },
                ],
            },
            "references": [],
            "status": "ok",
        }
        aporte = {
            "resumen": "El pozo RB-IA-2191 registra 80,6 BOPD.",
            "explicacion": (
                "El pozo RB-IA-2191 registra 80,6 BOPD. "
                "Estos valores corresponden a las mediciones registradas."
            ),
        }
        salida = fusionar_linguistica(contrato, aporte)
        plano = texto_plano(salida)
        # Una sola aparición dominante del valor en prosa (tabla aparte).
        self.assertLessEqual(plano.count("80,6 BOPD"), 2)
        paras = [
            b.get("text") for b in salida["answer"]["blocks"]
            if b.get("type") == "paragraph"
        ]
        # No deben coexistir el párrafo stock y el del modelo diciendo lo mismo.
        self.assertTrue(aporta_novedad.__doc__)
        self.assertLessEqual(len(paras), 1)


class EnsambleIntegridadTests(TestCase):
    def test_caudal_total_no_usa_none(self):
        decision = interpretar(
            "caudal total de fluidos",
            pozo_formulario="RB-1521",
            ambito="pozo",
        )
        self.assertEqual(decision["intencion"], "caudal")
        guardar({
            "pozo_id": "RB-1521",
            "dataset_id": "RB-1521",
            "escenario_id": "base-RB-1521",
            "evaluacion_id": "base-RB-1521",
            "emitido_en": "2026-10-31T18:00:00+00:00",
            "modo": "escenario_inicial",
            "origen_valores": "hoja",
            "estado": {"codigo": "SIN_DATOS", "rotulo": "REGISTRO", "tono": "sin-clasificacion", "clasificacion_valida": False},
            "texto": {"mensaje": "registro", "accion": "", "nota": "", "origen": "deterministico"},
            "resultados": {
                "q_fluidos": {"valor": 8977.0, "valor_visible": "8977", "unidad": "BFPD", "nombre": "Q-fluidos"},
                "q_water": {"valor": 8842.345, "valor_visible": "8842.34", "unidad": "BWPD", "nombre": "Q-water"},
            },
            "reglas_activas": [],
            "recomendacion_operacional_autorizada": False,
            "entradas": {},
        })
        modelo = _Modelo('{"resumen":"El caudal total es 8977 BFPD.","explicacion":""}')
        salida = responder(
            "caudal total de fluidos",
            "RB-1521",
            {},
            modelo,
            modelo="m",
            num_predict=64,
            dataset_id="RB-1521",
            ambito="pozo",
            alcance={"dataset": "RB-1521", "pozo": "RB-1521"},
        )
        texto = (salida.get("inferencia") or {}).get("contenido") or ""
        self.assertNotIn("None", texto)
        self.assertIn("8977", texto.replace(".", "").replace(",", ""))

    def test_respuesta_bopd_sin_parrafo_duplicado(self):
        guardar({
            "pozo_id": "RB-IA-2191",
            "dataset_id": "RB-IA-2191",
            "escenario_id": "base-RB-IA-2191",
            "evaluacion_id": "base-RB-IA-2191",
            "emitido_en": "2026-10-31T18:00:00+00:00",
            "modo": "escenario_inicial",
            "origen_valores": "hoja",
            "estado": {"codigo": "SIN_DATOS", "rotulo": "REGISTRO", "tono": "sin-clasificacion", "clasificacion_valida": False},
            "texto": {"mensaje": "registro", "accion": "", "nota": "", "origen": "deterministico"},
            "resultados": {
                "bfpd": {"valor": 5180.0, "valor_visible": "5180", "unidad": "BFPD", "nombre": "BFPD"},
                "bwpd": {"valor": 5099.4, "valor_visible": "5099.4", "unidad": "BWPD", "nombre": "BWPD"},
                "bopd": {"valor": 80.6, "valor_visible": "80.6", "unidad": "BOPD", "nombre": "BOPD"},
            },
            "reglas_activas": [],
            "recomendacion_operacional_autorizada": False,
            "entradas": {},
        })
        modelo = _Modelo(
            '{"resumen":"El BOPD del pozo RB-IA-2191 es 80,6 BOPD.",'
            '"explicacion":"El BOPD del pozo RB-IA-2191 es 80,6 BOPD. '
            'Estos valores corresponden a las mediciones registradas."}'
        )
        salida = responder(
            "¿Cuál es el BOPD?",
            "RB-IA-2191",
            {},
            modelo,
            modelo="m",
            num_predict=64,
            dataset_id="RB-IA-2191",
            ambito="pozo",
            alcance={"dataset": "RB-IA-2191", "pozo": "RB-IA-2191"},
        )
        texto = (salida.get("inferencia") or {}).get("contenido") or ""
        # La explicación duplicada del modelo no debe aparecer completa dos veces.
        self.assertEqual(texto.count("Estos valores corresponden"), 0)
        self.assertIn("80,6 BOPD", texto)
        self.assertNotIn("80,6 BFPD", texto)

    def test_comparar_rb_no_imprime_none(self):
        for pozo, resultados in (
            ("RB-1521", {
                "q_fluidos": {"valor": 8977.0, "valor_visible": "8977", "unidad": "BFPD", "nombre": "Q-fluidos"},
                "q_water": {"valor": 8842.345, "valor_visible": "8842.34", "unidad": "BWPD", "nombre": "Q-water"},
            }),
            ("RB-IA-2191", {
                "bfpd": {"valor": 5180.0, "valor_visible": "5180", "unidad": "BFPD", "nombre": "BFPD"},
                "pip": {"valor": 704.0, "valor_visible": "704", "unidad": "ft", "nombre": "PIP"},
            }),
        ):
            guardar({
                "pozo_id": pozo,
                "dataset_id": pozo,
                "escenario_id": f"base-{pozo}",
                "evaluacion_id": f"base-{pozo}",
                "emitido_en": "2026-10-31T18:00:00+00:00",
                "modo": "escenario_inicial",
                "origen_valores": "hoja",
                "estado": {"codigo": "SIN_DATOS", "rotulo": "REGISTRO", "tono": "sin-clasificacion", "clasificacion_valida": False},
                "texto": {"mensaje": "registro", "accion": "", "nota": "", "origen": "deterministico"},
                "resultados": resultados,
                "reglas_activas": [],
                "recomendacion_operacional_autorizada": False,
                "entradas": {},
            })
        modelo = _Modelo('{"resumen":"Comparación publicada.","explicacion":""}')
        salida = responder(
            "compara RB-1521 y RB-IA-2191",
            None,
            {},
            modelo,
            modelo="m",
            num_predict=64,
            dataset_id="ALL",
            ambito="dataset",
            alcance={"dataset": "Todos", "pozo": "Todos"},
        )
        texto = (salida.get("inferencia") or {}).get("contenido") or ""
        self.assertNotIn("None", texto)
        self.assertIn("RB-1521", texto)
        self.assertIn("RB-IA-2191", texto)
        self.assertTrue("8977" in texto or "5180" in texto or "704" in texto)

    def test_eficiencia_no_repite_aviso(self):
        modelo = _Modelo('{"resumen":"x","explicacion":""}')
        salida = responder(
            "¿Cuál es la eficiencia de QF-084?",
            "QF-084",
            {},
            modelo,
            modelo="m",
            num_predict=64,
            dataset_id="BES-jun",
            ambito="pozo",
            alcance={"dataset": "BES-jun", "pozo": "QF-084"},
        )
        texto = (salida.get("inferencia") or {}).get("contenido") or ""
        self.assertEqual(texto.count("No tengo una eficiencia validada"), 1)
