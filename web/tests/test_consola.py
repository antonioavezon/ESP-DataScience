import hashlib
import json
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, override_settings

from services.estado_operacional import clasificar, respuesta_obsoleta
from services.formato_numero import formato_visible
from services.escenario_inicial import escenario_de, listar_pozos, localizar
from services.mensajes_operador import _compatible, explicar
from services.ollama_client import Inferencia

RAIZ = Path(__file__).resolve().parents[2]
EXCEL = RAIZ / "datasets" / "en_uso" / "BES-jun" / "entrada" / "BES_jun.xlsx"
ORIGINAL = RAIZ / "fuentes" / "originales" / "Copia de FINAL BES-jun.xlsx"
HASH = "ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85"


def _sha(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


@override_settings(ALLOWED_HOSTS=["127.0.0.1", "localhost", "testserver"])
class ConsolaOperacionalTests(TestCase):
    def test_pozos_reales_y_escenario_inicial(self):
        lista = self.client.get("/api/consola/pozos/").json()["pozos"]
        identificadores = [item["pozo_id"] for item in lista]
        bes = ["QF-084", "QF-301", "QF-147", "QF-005", "QF-306"]
        self.assertEqual([item for item in identificadores if item in bes], bes)
        self.assertIn("RB-1521", identificadores)
        self.assertNotIn("Pozo demo", identificadores)
        ficha, pozo = localizar("QF-084")[0]
        escenario = escenario_de(pozo, ficha)
        self.assertNotIn("telemetría", escenario["leyenda"])
        identificadores_controles = [item["id"] for item in escenario["controles"]]
        self.assertEqual(identificadores_controles, ["frecuencia_hz", "caudal_operacion_bfpd"])
        self.assertNotIn("tvd_intake_ft", identificadores_controles)
        frecuencia = escenario["controles"][0]
        caudal = escenario["controles"][1]
        self.assertEqual(frecuencia["valor_inicial"], 63.0)
        self.assertEqual(frecuencia["unidad"], "Hz")
        self.assertEqual(frecuencia["recorrido"]["minimo"], 56.0)
        self.assertEqual(frecuencia["recorrido"]["maximo"], 67.0)
        self.assertFalse(frecuencia["recorrido"]["es_limite_operacional"])
        self.assertEqual(caudal["valor_inicial"], 10301.0)
        self.assertEqual(caudal["unidad"], "BFPD")
        self.assertIn("RC-BES-01", caudal["reglas"])
        self.assertGreater(caudal["recorrido"]["maximo"], caudal["recorrido"]["limite_maximo"])
        self.assertLess(caudal["recorrido"]["minimo"], caudal["recorrido"]["limite_minimo"])
        self.assertIsNone(escenario["fecha_medicion"])
        self.assertNotIn("potencia", [item["id"] for item in escenario["lecturas"]])

    def test_cada_pozo_conserva_su_frecuencia(self):
        esperadas = {"QF-084": 63.0, "QF-301": 57.0, "QF-147": 56.0, "QF-005": 67.0, "QF-306": 62.0}
        for pozo_id, frecuencia in esperadas.items():
            ficha, pozo = localizar(pozo_id)[0]
            control = next(item for item in escenario_de(pozo, ficha)["controles"] if item["id"] == "frecuencia_hz")
            self.assertEqual(control["valor_inicial"], frecuencia)

    def test_evaluacion_inicial_no_es_correcto(self):
        antes = _sha(EXCEL)
        respuesta = self._evaluar("QF-084", {})
        self.assertEqual(respuesta["estado"]["codigo"], "NORMAL")
        self.assertTrue(respuesta["estado"]["clasificacion_valida"])
        self.assertIn("RC-BES-03", respuesta["reglas_activas"])
        self.assertNotIn("RC-BES-01", respuesta["reglas_activas"])
        self.assertFalse(respuesta["recomendacion_operacional_autorizada"])
        self.assertNotIn("SIN CLASIFICACIÓN", respuesta["estado"]["rotulo"])
        self.assertNotIn("condición correcta", respuesta["texto"]["mensaje"])
        self.assertNotIn("telemetría", respuesta["leyenda"])
        from services.formato_numero import formato_visible
        pip = respuesta["resultados"]["pip_ft"]
        self.assertGreater(len(str(pip["valor"]).split(".")[-1]), 2)
        self.assertEqual(pip["valor_visible"], formato_visible(pip["valor"]))
        self.assertNotEqual(pip["valor_visible"], str(pip["valor"]))
        self.assertEqual(respuesta["modo"], "escenario_inicial")
        self.assertIsNotNone(respuesta["resultados"]["pip_ft"]["valor"])
        self.assertEqual(_sha(EXCEL), antes)
        self.assertEqual(_sha(ORIGINAL), HASH)

    def test_cambiar_frecuencia_cambia_la_regla(self):
        respuesta = self._evaluar("QF-084", {"frecuencia_hz": 60})
        self.assertEqual(respuesta["modo"], "simulacion")
        self.assertIn("RC-BES-01", respuesta["reglas_activas"])
        self.assertNotIn("RC-BES-03", respuesta["reglas_activas"])
        self.assertEqual(respuesta["estado"]["codigo"], "INCIPIENTE")
        self.assertTrue(respuesta["estado"]["clasificacion_valida"])
        self.assertNotEqual(respuesta["estado"]["codigo"], "CRITICO")
        self.assertEqual(respuesta["estado"]["condicion"], "fuera_del_texto_de_la_hoja")
        self.assertIn("supera el máximo escrito", respuesta["texto"]["mensaje"])
        self.assertNotIn("validado", respuesta["texto"]["accion"])
        self.assertIn("frecuencia_hz", respuesta["modificadas"])

    def test_la_profundidad_no_es_mando_de_las_reglas(self):
        antes = _sha(EXCEL)
        codigo, cuerpo = self._post("QF-084", {"tvd_intake_ft": 2700})
        self.assertEqual(codigo, 400)
        self.assertIn("no es un mando", cuerpo["error"])
        self.assertEqual(_sha(EXCEL), antes)

    def test_el_caudal_cruza_el_limite_escrito_y_vuelve(self):
        dentro = self._evaluar("QF-084", {"caudal_operacion_bfpd": 10500})
        self.assertEqual(dentro["estado"]["codigo"], "NORMAL")
        self.assertIn("RC-BES-03", dentro["reglas_activas"])
        fuera = self._evaluar("QF-084", {"caudal_operacion_bfpd": 10501})
        self.assertEqual(fuera["estado"]["codigo"], "INCIPIENTE")
        self.assertIn("RC-BES-01", fuera["reglas_activas"])
        self.assertNotEqual(fuera["estado"]["codigo"], "CRITICO")
        regreso = self._evaluar("QF-084", {"caudal_operacion_bfpd": 10301})
        self.assertEqual(regreso["estado"]["codigo"], "NORMAL")
        self.assertEqual(len([regla for regla in ("RC-BES-01", "RC-BES-02", "RC-BES-03") if regla in fuera["reglas_activas"]]), 1)

    def test_potencia_y_head_no_son_entradas(self):
        codigo, cuerpo = self._post("QF-084", {"potencia": 100, "head": 2000})
        self.assertEqual(codigo, 400)
        self.assertIn("no es un mando", cuerpo["error"])

    def test_unidad_y_rango(self):
        codigo, cuerpo = self._post("QF-084", {"frecuencia_hz": {"valor": 60, "unidad": "psi"}})
        self.assertEqual(codigo, 400)
        self.assertIn("Hz", cuerpo["error"])
        codigo, cuerpo = self._post("QF-084", {"frecuencia_hz": 0})
        self.assertEqual(codigo, 400)
        self.assertIn("mayor que cero", cuerpo["error"])
        codigo, cuerpo = self._post("QF-084", {"frecuencia_hz": "alto"})
        self.assertEqual(codigo, 400)
        self.assertIn("no es un número", cuerpo["error"])

    def test_pozo_desconocido_y_restauracion(self):
        self.assertEqual(self.client.get("/api/consola/pozos/QF-999/escenario/").status_code, 404)
        restaurado = self._evaluar("QF-084", {"frecuencia_hz": 63})
        self.assertEqual(restaurado["modificadas"], [])
        self.assertEqual(restaurado["modo"], "escenario_inicial")

    def test_clasificacion_sintetica_no_es_una_medicion(self):
        peligro = clasificar({
            "estado_evaluacion": "completada_preliminar",
            "recomendacion_operacional_autorizada": False,
            "reglas": [{
                "id": "REGLA-SINTETICA-PRUEBA",
                "activada": True,
                "aprobada_para_uso_operacional": True,
                "limite_critico_validado": True,
            }],
        })
        self.assertEqual(peligro["codigo"], "CRITICO")
        self.assertTrue(peligro["clasificacion_valida"])
        correcto = clasificar({
            "estado_evaluacion": "completada_preliminar",
            "recomendacion_operacional_autorizada": True,
            "reglas": [{
                "id": "RC-BES-03",
                "activada": True,
                "aprobada_para_uso_operacional": True,
                "limite_critico_validado": False,
            }],
        })
        self.assertEqual(correcto["codigo"], "NORMAL")
        self.assertTrue(correcto["clasificacion_valida"])
        incipiente = clasificar({
            "estado_evaluacion": "completada_preliminar",
            "recomendacion_operacional_autorizada": False,
            "reglas": [{
                "id": "REGLA-SINTETICA-ALERTA",
                "activada": True,
                "aprobada_para_uso_operacional": False,
                "alerta_temprana": True,
                "limite_critico_validado": False,
            }],
        })
        self.assertEqual(incipiente["codigo"], "INCIPIENTE")
        self.assertFalse(incipiente["aprobadas"])
        sin_datos = clasificar({"estado_evaluacion": "no_evaluable", "reglas": []})
        self.assertEqual(sin_datos["codigo"], "SIN_DATOS")
        self.assertFalse(sin_datos["clasificacion_valida"])
        error = clasificar({"estado_evaluacion": "entrada_invalida", "reglas": []})
        self.assertEqual(error["codigo"], "ERROR_CALCULO")
        self.assertNotIn(error["codigo"], ("NORMAL", "INCIPIENTE", "CRITICO"))
        self.assertEqual(formato_visible(2570.87200657892), "2570.87")
        self.assertEqual(formato_visible(60.0), "60")
        self.assertEqual(formato_visible(45.567891), "45.57")
        self.assertEqual(formato_visible(12.5), "12.5")
        self.assertEqual(formato_visible(0.123456), "0.12")
        self.assertTrue(respuesta_obsoleta("1", "2"))
        self.assertFalse(respuesta_obsoleta("2", "2"))

    def test_ollama_no_cambia_el_estado_y_cae_al_respaldo(self):
        class Habla:
            def __init__(self, *args, **kwargs):
                pass
            def cerrar(self):
                return None
            def consultar(self, modelo, mensajes, num_predict):
                return Inferencia(ok=True, contenido="La bomba está segura y en estado correcto.", modelo=modelo, done_reason="stop")

        with patch("services.mensajes_operador.ClienteOllama", Habla):
            codigo, cuerpo = self._post("QF-084", {}, explicar=True)
        self.assertEqual(codigo, 200)
        self.assertEqual(cuerpo["estado"]["codigo"], "NORMAL")
        self.assertEqual(cuerpo["texto"]["origen"], "deterministico")
        self.assertNotIn("está segura", cuerpo["texto"]["mensaje"])

    def test_ollama_caido_e_incompleto(self):
        class Caido:
            def __init__(self, *args, **kwargs):
                pass
            def cerrar(self):
                return None
            def consultar(self, modelo, mensajes, num_predict):
                return Inferencia(ok=False, error="Ollama no está disponible: ConnectError.")

        with patch("services.mensajes_operador.ClienteOllama", Caido):
            cuerpo = self._post("QF-084", {}, explicar=True)[1]
        self.assertEqual(cuerpo["texto"]["origen"], "deterministico")
        self.assertEqual(cuerpo["estado_fijado_por"], "motor")

        class Incompleto:
            def __init__(self, *args, **kwargs):
                pass
            def cerrar(self):
                return None
            def consultar(self, modelo, mensajes, num_predict):
                return Inferencia(ok=True, contenido="texto parcial", incompleta=True, done_reason="length", modelo=modelo)

        with patch("services.mensajes_operador.ClienteOllama", Incompleto):
            cuerpo = self._post("QF-084", {}, explicar=True)[1]
        self.assertEqual(cuerpo["texto"]["origen"], "deterministico")
        self.assertFalse(_compatible("", "SIN_CLASIFICACION"))
        self.assertFalse(_compatible(
            "El caudal no cumple con los límites establecidos en la hoja.",
            {"codigo": "ADVERTENCIA", "condicion": "dentro_del_texto_de_la_hoja"},
        ))

    def test_explicar_rechaza_cifra_nueva(self):
        class Inventa:
            def __init__(self, *args, **kwargs):
                pass
            def cerrar(self):
                return None
            def consultar(self, modelo, mensajes, num_predict):
                return Inferencia(ok=True, contenido="El caudal llegó a 99999 BFPD.", incompleta=False, done_reason="stop", modelo=modelo)

        respaldo = {"mensaje": "El caudal está entre el mínimo y el máximo escritos a esta frecuencia.", "accion": "", "nota": ""}
        with patch("services.mensajes_operador.ClienteOllama", Inventa):
            salida = explicar({"codigo": "NORMAL", "rotulo": "NORMAL", "condicion": "dentro_de_los_limites_escritos", "reglas": []}, respaldo, [], {})
        self.assertEqual(salida["origen"], "deterministico")
        self.assertNotIn("99999", salida["mensaje"])

    def test_estados_iniciales_no_inventan_color(self):
        from services.consola_operacional import estados_iniciales
        with patch("services.mensajes_operador.ClienteOllama", side_effect=AssertionError("el menu no consulta al asistente")):
            cuerpo = estados_iniciales()
        respuesta = self.client.get("/api/consola/estados/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.json()["proceso_disponible"])
        identificadores = [fila["pozo_id"] for fila in cuerpo["pozos"]]
        bes = ["QF-084", "QF-301", "QF-147", "QF-005", "QF-306"]
        self.assertEqual([item for item in identificadores if item in bes], bes)
        self.assertIn("RB-1521", identificadores)
        self.assertEqual(len(set(identificadores)), len(identificadores))
        self.assertNotIn("CSV histórico", json.dumps(cuerpo))
        self.assertNotIn("SIN CLASIFICACIÓN", json.dumps(cuerpo))
        for fila in cuerpo["pozos"]:
            self.assertEqual(fila["origen"], "escenario_inicial")
            if fila["clasificacion_valida"]:
                self.assertIn(fila["codigo"], ("NORMAL", "INCIPIENTE", "CRITICO"))
                self.assertIn(fila["tono"], ("normal", "incipiente", "critico"))
            else:
                self.assertEqual(fila["tono"], "sin-clasificacion")
                self.assertNotIn(fila["codigo"], ("NORMAL", "INCIPIENTE", "CRITICO"))
        qf084 = next(fila for fila in cuerpo["pozos"] if fila["pozo_id"] == "QF-084")
        self.assertEqual(qf084["codigo"], "NORMAL")
        self.assertTrue(qf084["clasificacion_valida"])
        sin_regla = {"RB-1521", "RB-IA-2191"}
        self.assertTrue(
            all(fila["codigo"] == "NORMAL" for fila in cuerpo["pozos"] if fila["pozo_id"] not in sin_regla)
        )
        for pozo_id in sin_regla:
            registro = next(fila for fila in cuerpo["pozos"] if fila["pozo_id"] == pozo_id)
            self.assertEqual(registro["rotulo"], "REGISTRO")
            self.assertFalse(registro["clasificacion_valida"])
        self.assertNotIn("ollama", json.dumps(cuerpo).lower())
        self.assertEqual(_sha(EXCEL), HASH)
        self.assertEqual(_sha(ORIGINAL), HASH)

    def test_el_cliente_descarta_respuestas_viejas(self):
        texto = (Path(__file__).resolve().parents[1] / "static" / "js" / "consola.js").read_text(encoding="utf-8")
        mandos = (Path(__file__).resolve().parents[1] / "static" / "js" / "mandos.js").read_text(encoding="utf-8")
        self.assertIn("cuerpo.evaluacion_id", texto)
        self.assertIn("AbortController", texto)
        self.assertIn(">Inicio<", mandos)
        self.assertIn("numero.value = formatoVisible(numeroNuevo)", mandos)
        self.assertNotIn("type='range'", texto)
        self.assertNotIn("Evaluar escenario", texto)
        self.assertNotIn("Restaurar este mando", texto)
        self.assertNotIn("Restaurar valores iniciales", texto)
        estilos = (Path(__file__).resolve().parents[1] / "static" / "css" / "app.css").read_text(encoding="utf-8")
        self.assertIn("grid-template-columns: repeat(3, minmax(0, 1fr))", estilos)
        self.assertIn("repeat(2, minmax(0, 1fr))", estilos)
        self.assertIn("max-width: 560px", estilos)
        self.assertIn("huc-estado", texto)
        self.assertIn("huc.escenarios", texto)
        menu = (Path(__file__).resolve().parents[1] / "static" / "js" / "pozos_menu.js").read_text(encoding="utf-8")
        self.assertIn("clasificacion_valida", menu)
        self.assertNotIn("alternar-menu", menu)
        self.assertNotIn("ollama", menu.lower())
        self.assertNotIn("qwen", menu.lower())

    def _evaluar(self, pozo, controles):
        codigo, cuerpo = self._post(pozo, controles)
        self.assertEqual(codigo, 200, cuerpo)
        return cuerpo

    def _post(self, pozo, controles, explicar=False):
        from proceso.motores.ejecutor import evaluar

        return evaluar(pozo, controles, "esc-prueba", "ev-prueba", explicar)
