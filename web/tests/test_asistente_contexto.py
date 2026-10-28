"""Contexto dual (dataset × pozo) y presentación estructurada del asistente."""

from unittest.mock import patch

from django.test import TestCase

from services.chat_intencion import interpretar
from services.chat_orquestador import responder
from services.chat_presentacion import etiqueta_alcance, estructurar, render_html
from services.consola_operacional import evaluar_pozo
from services.ollama_client import Inferencia


class _Modelo:
    def __init__(self, contenido="", ok=True):
        self.contenido = contenido
        self.ok = ok
        self.llamadas = 0

    def consultar(self, modelo, mensajes, num_predict):
        self.llamadas += 1
        return Inferencia(ok=self.ok, contenido=self.contenido, error="", modelo=modelo, done_reason="stop")

    def cerrar(self):
        return None


def _preguntar(consulta, pozo=None, ambito=None, dataset_id="BES-jun", modelo=None, alcance=None):
    if ambito is None:
        ambito = "pozo" if pozo else "dataset"
    if alcance is None:
        alcance = {
            "dataset": "Todos" if dataset_id in (None, "", "ALL", "all", "Todos") else dataset_id,
            "pozo": pozo or "Todos",
        }
    return responder(
        consulta,
        pozo,
        {},
        modelo or _Modelo(),
        modelo="modelo-prueba",
        num_predict=64,
        dataset_id=dataset_id,
        ambito=ambito,
        alcance=alcance,
    )


class IntencionNaturalTests(TestCase):
    def test_estado_con_pozo_seleccionado(self):
        decision = interpretar("¿Cómo está el pozo?", {}, "QF-084", "pozo")
        self.assertEqual(decision["intencion"], "estado")
        self.assertEqual(decision["pozos"], ["QF-084"])

    def test_estado_sin_pozo_usa_dataset(self):
        decision = interpretar("¿Cómo están los pozos?", {}, None, "dataset")
        self.assertEqual(decision["intencion"], "estado")
        self.assertEqual(decision["pozos"], [])

    def test_medidas_y_presiones(self):
        self.assertEqual(interpretar("¿Qué medidas tiene?", {}, "QF-084", "pozo")["intencion"], "medidas")
        self.assertEqual(interpretar("¿Qué niveles de presión tiene?", {}, "QF-084", "pozo")["intencion"], "presiones")
        self.assertEqual(interpretar("¿Cuál es su caudal?", {}, "QF-084", "pozo")["intencion"], "caudal")

    def test_seguimiento_sin_repetir_pozo(self):
        decision = interpretar("¿Y su presión?", {"pozo": "QF-084"}, "QF-084", "pozo")
        self.assertEqual(decision["intencion"], "seguimiento")
        self.assertEqual(decision["pozos"], ["QF-084"])


class RespuestasRealesTests(TestCase):
    def test_como_esta_qf084(self):
        salida = _preguntar("¿Cómo está el pozo?", pozo="QF-084")
        texto = salida["inferencia"]["contenido"]
        codigo, cuerpo = evaluar_pozo("QF-084", {}, "ref", "ref", False)
        self.assertEqual(codigo, 200)
        self.assertIn("QF-084", texto)
        self.assertIn(cuerpo["estado"]["rotulo"], texto)
        self.assertIn("NORMAL", texto)
        self.assertIsNotNone(salida["inferencia"].get("estructura"))
        self.assertEqual(salida["inferencia"]["alcance"]["dataset"], "BES-jun")
        self.assertNotIn("RC-BES", texto)
        self.assertNotIn("otro tipo de pozo", texto.lower())

    def test_medidas_qf084(self):
        salida = _preguntar("¿Qué medidas tiene?", pozo="QF-084")
        texto = salida["inferencia"]["contenido"]
        self.assertIn("QF-084", texto)
        self.assertIn("Hz", texto)
        self.assertIn("BFPD", texto)
        self.assertIn("ft", texto)

    def test_presiones_distinguen_unidades(self):
        salida = _preguntar("¿Qué niveles de presión tiene?", pozo="QF-084")
        texto = salida["inferencia"]["contenido"]
        self.assertIn("QF-084", texto)
        self.assertTrue("psi" in texto or "pies de fluido" in texto or "ft" in texto)

    def test_todos_los_pozos_bes_jun(self):
        salida = _preguntar("¿Cómo están los pozos?", dataset_id="BES-jun")
        texto = salida["inferencia"]["contenido"]
        estructura = salida["inferencia"]["estructura"]
        self.assertIn("QF-084", texto)
        self.assertIn("QF-301", texto)
        self.assertIn("NORMAL", texto)
        self.assertEqual(estructura["schema_version"], "1.0")
        self.assertEqual(estructura["answer"]["type"], "wells_summary")
        self.assertTrue(any(b.get("type") == "table" for b in estructura["answer"]["blocks"]))
        self.assertEqual(salida["inferencia"]["alcance"]["dataset"], "BES-jun")

    def test_contexto_global_no_sustituye_bes_jun(self):
        alcance = {"dataset": "Todos", "pozo": "Todos"}
        salida = _preguntar("¿Cómo están los pozos?", dataset_id="ALL", alcance=alcance)
        self.assertEqual(salida["inferencia"]["alcance"]["dataset"], "Todos")
        self.assertEqual(salida["inferencia"]["alcance"]["pozo"], "Todos")
        self.assertIn("BES-jun", salida["inferencia"]["contenido"])
        self.assertIn("QF-084", salida["inferencia"]["contenido"])
        self.assertIn("Proceden de", salida["inferencia"]["estructura"]["answer"]["summary"])

    def test_cuantos_pozos_inventario_global(self):
        salida = _preguntar("¿Cuántos pozos hay?", dataset_id="ALL", alcance={"dataset": "Todos", "pozo": "Todos"})
        self.assertEqual(salida["inferencia"]["estructura"]["answer"]["type"], "inventory")
        self.assertIn("pozos registrados", salida["inferencia"]["contenido"].lower())

    def test_bombas_sin_negacion_irrelevante(self):
        salida = _preguntar("¿Qué bombas utilizan?")
        texto = salida["inferencia"]["contenido"]
        self.assertIn("bombeo electrosumergible", texto)
        self.assertNotIn("otro tipo", texto.lower())
        self.assertNotIn("no hay en las hojas", texto.lower())

    def test_ollama_caido_conserva_hechos(self):
        salida = _preguntar("¿Cómo está el pozo?", pozo="QF-084", modelo=_Modelo(ok=False))
        self.assertIn("QF-084", salida["inferencia"]["contenido"])

    def test_modelo_duplicado_no_concatena(self):
        hechos = _preguntar("¿Cómo está el pozo?", pozo="QF-084", modelo=_Modelo(ok=False))["inferencia"]["contenido"]
        salida = _preguntar("¿Cómo está el pozo?", pozo="QF-084", modelo=_Modelo(hechos))
        self.assertEqual(salida["inferencia"]["contenido"].count(hechos), 1)


class PresentacionEstructuradaTests(TestCase):
    def test_etiqueta_alcance(self):
        self.assertEqual(etiqueta_alcance({"dataset": "Todos", "pozo": "Todos"}), "Dataset: Todos · Pozos: Todos")
        self.assertEqual(etiqueta_alcance({"dataset": "BES-jun", "pozo": "Todos"}), "Dataset: BES-jun · Pozos: Todos")
        self.assertEqual(etiqueta_alcance({"dataset": "BES-jun", "pozo": "QF-084"}), "Dataset: BES-jun · Pozo: QF-084")
        self.assertNotIn("Sin pozo", etiqueta_alcance({"dataset": "Todos", "pozo": "Todos"}))

    def test_html_seguro_con_tabla(self):
        estructura = estructurar(
            "estado",
            [{
                "pozo": "QF-084",
                "dataset_id": "BES-jun",
                "rotulo": "NORMAL",
                "magnitudes": [
                    {"id": "frecuencia_hz", "nombre": "Frecuencia", "visible": "63", "unidad": "Hz"},
                    {"id": "caudal_a_producir_bfpd", "nombre": "Caudal", "visible": "10535.17", "unidad": "BFPD"},
                ],
            }, {
                "pozo": "QF-301",
                "dataset_id": "BES-jun",
                "rotulo": "NORMAL",
                "magnitudes": [
                    {"id": "frecuencia_hz", "nombre": "Frecuencia", "visible": "57", "unidad": "Hz"},
                    {"id": "caudal_a_producir_bfpd", "nombre": "Caudal", "visible": "8280.86", "unidad": "BFPD"},
                ],
            }],
            dataset_id="BES-jun",
            alcance={"dataset": "BES-jun", "pozo": "Todos"},
        )
        html = render_html(estructura)
        self.assertIn('<table class="asistente-tabla">', html)
        self.assertIn("<th>Pozo</th>", html)
        self.assertIn("QF-084", html)
        self.assertNotIn("<script>", html)

    def test_html_escapa_contenido(self):
        html = render_html({
            "titulo": '<img src=x onerror=alert(1)>',
            "resumen": "A & B",
            "secciones": [],
            "explicacion": "",
        })
        self.assertNotIn("<img", html)
        self.assertIn("&lt;img", html)
        self.assertIn("A &amp; B", html)


class VistaAsistenteTests(TestCase):
    def test_pagina_por_defecto_es_todos(self):
        pagina = self.client.get("/asistente/")
        self.assertContains(pagina, "Dataset: Todos · Pozos: Todos")
        self.assertContains(pagina, 'name="dataset_id"')
        self.assertContains(pagina, 'name="pozo_id"')
        self.assertContains(pagina, "Todos los pozos")

    def test_selector_dataset_bes_jun(self):
        pagina = self.client.get("/asistente/?dataset_id=BES-jun", follow=True)
        self.assertContains(pagina, "Dataset: BES-jun · Pozos: Todos")

    def test_consulta_global_conserva_alcance(self):
        with patch("apps.asistente_ia.views.ClienteOllama", _Modelo):
            respuesta = self.client.post("/asistente/enviar/", {
                "consulta": "¿Cómo están los pozos?",
                "dataset_id": "ALL",
                "pozo_id": "",
            }, follow=True)
        self.assertContains(respuesta, "Dataset: Todos · Pozos: Todos")
        self.assertContains(respuesta, "asistente-tabla")
        self.assertContains(respuesta, "QF-084")
        self.assertContains(respuesta, "NORMAL")
        self.assertNotContains(respuesta, "Sin pozo")

    def test_consulta_bes_jun_todos(self):
        with patch("apps.asistente_ia.views.ClienteOllama", _Modelo):
            respuesta = self.client.post("/asistente/enviar/", {
                "consulta": "¿Cómo están los pozos de BES-jun?",
                "dataset_id": "BES-jun",
                "pozo_id": "",
            }, follow=True)
        self.assertContains(respuesta, "Dataset: BES-jun · Pozos: Todos")
        self.assertContains(respuesta, "asistente-tabla")

    def test_consulta_pozo_especifico(self):
        with patch("apps.asistente_ia.views.ClienteOllama", _Modelo):
            respuesta = self.client.post("/asistente/enviar/", {
                "consulta": "¿Cómo está el pozo?",
                "dataset_id": "BES-jun",
                "pozo_id": "QF-084",
            }, follow=True)
        self.assertContains(respuesta, "Dataset: BES-jun · Pozo: QF-084")
        self.assertContains(respuesta, "QF-084")
        self.assertContains(respuesta, "NORMAL")

    def test_presion_pozo_qf301(self):
        with patch("apps.asistente_ia.views.ClienteOllama", _Modelo):
            respuesta = self.client.post("/asistente/enviar/", {
                "consulta": "¿Qué presión tiene?",
                "dataset_id": "BES-jun",
                "pozo_id": "QF-301",
            }, follow=True)
        self.assertContains(respuesta, "Dataset: BES-jun · Pozo: QF-301")
        self.assertContains(respuesta, "QF-301")
