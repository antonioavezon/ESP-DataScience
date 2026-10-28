"""Respuestas a «por qué» de estado y caudal."""

from django.test import TestCase

from services.chat_explicaciones import explicar_caudal, explicar_estado
from services.chat_intencion import interpretar
from services.chat_orquestador import responder
from services.ollama_client import Inferencia


class _Modelo:
    def __init__(self, *args, **kwargs):
        pass

    def consultar(self, *args, **kwargs):
        return Inferencia(
            ok=True,
            contenido='{"resumen":"Explicación breve.","explicacion":"Detalle seguro."}',
            modelo="modelo-prueba",
            done_reason="stop",
        )

    def cerrar(self):
        return None


class ExplicacionesPorqueTests(TestCase):
    def test_intencion_porque_normal(self):
        d = interpretar("¿Por qué está en NORMAL?", {}, "QF-084", "pozo")
        self.assertEqual(d["intencion"], "estado")
        self.assertEqual(d["variable"], "motivo_estado")

    def test_intencion_porque_registro(self):
        d = interpretar('¿Por qué RB-1521 está en registro?', {}, None, "dataset")
        self.assertEqual(d["intencion"], "estado")
        self.assertEqual(d["pozos"], ["RB-1521"])
        self.assertEqual(d["variable"], "motivo_estado")

    def test_intencion_porque_caudal(self):
        d = interpretar("¿Por qué entrega ese caudal QF-084?", {}, None, "dataset")
        self.assertEqual(d["intencion"], "caudal")
        self.assertEqual(d["variable"], "motivo_caudal")
        self.assertEqual(d["pozos"], ["QF-084"])

    def test_texto_normal_incluye_limites(self):
        exp = explicar_estado({
            "pozo": "QF-084",
            "dataset_id": "BES-jun",
            "rotulo": "NORMAL",
            "magnitudes": [
                {"id": "frecuencia_hz", "visible": "63", "unidad": "Hz"},
                {"id": "caudal_a_producir_bfpd", "visible": "10535.17", "unidad": "BFPD"},
            ],
        })
        self.assertIn("NORMAL", exp["titulo"])
        self.assertTrue(any("Q_min" in f["expresion"] for f in exp["formulas"]))
        self.assertIn("mínimo", exp["resumen"].lower())

    def test_texto_registro_no_sin_procesar(self):
        exp = explicar_estado({
            "pozo": "RB-1521",
            "dataset_id": "RB-1521",
            "rotulo": "REGISTRO",
            "magnitudes": [],
        })
        blob = " ".join(exp["parrafos"] + [exp["resumen"], exp.get("cierre") or ""]).lower()
        self.assertIn("registro", exp["titulo"].lower())
        self.assertTrue("no indica" in blob or "no significa" in blob)
        self.assertTrue("regla de caudal" in blob or "umbrales de caudal" in blob)
        self.assertNotIn("sin procesar: sí", blob)
        # Evitar listar alternativas de estado en el resumen (provocaba badge falso).
        self.assertNotIn("incipiente", exp["resumen"].lower())
        self.assertNotIn("crítico", exp["resumen"].lower())

    def test_contrato_registro_badge_correcto(self):
        from services.chat_contrato import desde_estructura, render_html
        from services.chat_presentacion import estructurar

        fila = {
            "pozo": "RB-1521",
            "dataset_id": "RB-1521",
            "rotulo": "REGISTRO",
            "magnitudes": [
                {"id": "caudal_a_producir_bfpd", "visible": "8.977", "unidad": "BFPD"},
            ],
        }
        estructura = estructurar("motivo_estado", [fila], dataset_id="RB-1521", alcance={
            "dataset": "RB-1521", "pozo": "RB-1521",
        })
        contrato = desde_estructura(estructura, alcance={"dataset": "RB-1521", "pozo": "RB-1521"})
        estados = [b for b in contrato["answer"]["blocks"] if b.get("type") == "status"]
        self.assertEqual(len(estados), 1)
        self.assertEqual(estados[0]["label"], "REGISTRO")
        html = render_html(contrato)
        self.assertIn('data-estado="REGISTRO"', html)
        self.assertNotIn('data-estado="NORMAL"', html)
        # El cierre aparece una sola vez.
        self.assertEqual(html.lower().count("en resumen"), 1)

    def test_orquestador_porque_qf084(self):
        salida = responder(
            "¿Por qué está en NORMAL el pozo QF-084?",
            None,
            {},
            _Modelo(),
            modelo="modelo-prueba",
            num_predict=64,
            dataset_id="ALL",
            ambito="dataset",
            alcance={"dataset": "Todos", "pozo": "Todos"},
        )
        texto = salida["inferencia"]["contenido"]
        self.assertIn("NORMAL", texto)
        self.assertIn("QF-084", texto)
        self.assertTrue("mínimo" in texto.lower() or "Q_min" in texto)
        self.assertTrue("intersección" in texto.lower() or "fluido" in texto.lower() or "frecuencia" in texto.lower())
