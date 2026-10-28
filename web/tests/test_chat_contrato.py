"""Contrato de presentación versionado y render seguro."""

from django.test import TestCase

from services.chat_contrato import (
    SCHEMA_VERSION,
    contrato_vacio,
    desde_estructura,
    fusionar_linguistica,
    render_html,
    validar,
)


class ContratoPresentacionTests(TestCase):
    def test_valida_esquema_y_bloques(self):
        contrato = contrato_vacio(alcance={"dataset": "BES-jun", "pozo": "QF-084"}, tipo="well_status", titulo="Estado")
        contrato["answer"]["blocks"] = [
            {"type": "status", "label": "NORMAL", "text": "El pozo está en NORMAL."},
            {"type": "metrics", "items": [{"id": "pip_ft", "name": "PIP", "value": "1714.5", "unit": "ft", "origin": "motor"}]},
        ]
        ok, motivo = validar(contrato)
        self.assertTrue(ok, motivo)
        self.assertEqual(contrato["schema_version"], SCHEMA_VERSION)

    def test_rechaza_bloque_desconocido(self):
        contrato = contrato_vacio(alcance={}, tipo="notice")
        contrato["answer"]["blocks"] = [{"type": "iframe", "src": "x"}]
        ok, motivo = validar(contrato)
        self.assertFalse(ok)
        self.assertIn("bloque", motivo)

    def test_html_escapa_y_no_ejecuta(self):
        contrato = desde_estructura({
            "tipo": "estado_pozo",
            "titulo": "<script>x</script>",
            "resumen": "A & B",
            "secciones": [],
            "explicacion": "",
            "fuentes": ["BES-jun"],
        }, alcance={"dataset": "BES-jun", "pozo": "QF-084"})
        html = render_html(contrato)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>x</script>", html)
        self.assertIn("A &amp; B", html)

    def test_fusion_linguistica_no_toca_tabla(self):
        base = desde_estructura({
            "tipo": "estado_general",
            "titulo": "Estado",
            "resumen": "Resumen base",
            "secciones": [{
                "titulo": "T",
                "parrafos": [],
                "tabla": {"columnas": ["Pozo"], "filas": [["QF-084"]]},
                "lista": [],
            }],
            "explicacion": "",
            "fuentes": [],
        }, alcance={"dataset": "BES-jun", "pozo": "Todos"})
        fusion = fusionar_linguistica(base, {"resumen": "Nuevo resumen", "explicacion": "Detalle seguro"})
        self.assertEqual(fusion["answer"]["summary"], "Nuevo resumen")
        self.assertTrue(any(b.get("type") == "table" for b in fusion["answer"]["blocks"]))
        self.assertTrue(any(b.get("role") == "model" for b in fusion["answer"]["blocks"]))
