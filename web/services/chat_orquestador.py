"""Une la pregunta, el motor y la explicación. La pantalla no ve este recorrido."""

from __future__ import annotations

import sys
from pathlib import Path
import re

_RAIZ = Path(__file__).resolve().parents[2]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

from modelos_ia.redaccion import elegir
from services.chat_hechos import completar, corpus, pozos_de, redactar
from services.chat_herramientas import ejecutar
from services.chat_intencion import interpretar
from services.chat_contrato import (
    contrato_vacio,
    desde_estructura,
    fusionar_linguistica,
    render_html as render_contrato,
    texto_plano as texto_contrato,
    validar as validar_contrato,
)
from services.chat_presentacion import estructurar, etiqueta_alcance, texto_plano
from services.escenario_inicial import listar_pozos
from services.formato_numero import formato_visible
from services.ollama_client import ClienteOllama, configuracion
from services.technical_context import DEFINICION_PIP
import json

_CIFRA = re.compile(r"\d+\.\d+")
_FUENTE_PIP = "definición validada para el asistente de HUC"
_FUENTE_MOTOR = "cálculo del expediente en uso"


def responder(consulta: str, pozo_formulario: str | None, contexto: dict | None, cliente=None, modelo: str | None = None, num_predict: int | None = None, dataset_id: str | None = None, ambito: str | None = None, alcance: dict | None = None) -> dict:
    previo = contexto if isinstance(contexto, dict) else {}
    decision = interpretar(consulta, previo, pozo_formulario, ambito)
    # Dataset citado en el texto prima sobre «Todos» del selector; no sustituye un dataset ya elegido.
    datasets_texto = [d for d in (decision.get("datasets") or []) if d]
    if dataset_id in (None, "", "ALL", "all", "Todos") and len(datasets_texto) == 1:
        dataset_id = datasets_texto[0]
        alcance = {**(alcance or {}), "dataset": datasets_texto[0], "pozo": (alcance or {}).get("pozo") or "Todos"}
    # Pozo nombrado en la pregunta: el ámbito efectivo es ese pozo aunque el selector diga Todos.
    if decision.get("pozos"):
        ambito = "pozo"
        if alcance is not None and (not alcance.get("pozo") or alcance.get("pozo") in ("Todos", "ALL", "all", "")):
            alcance = {**alcance, "pozo": decision["pozos"][0]}
            if not alcance.get("dataset") or alcance.get("dataset") in ("Todos", "ALL", "all"):
                # Inferir dataset del pozo si hace falta.
                from services.escenario_inicial import listar_pozos
                for item in listar_pozos():
                    if item["pozo_id"] == decision["pozos"][0]:
                        alcance["dataset"] = item.get("dataset_id") or alcance.get("dataset") or "Todos"
                        if dataset_id in (None, "", "ALL", "all", "Todos"):
                            dataset_id = item.get("dataset_id") or dataset_id
                        break
    dataset_filtro = None if dataset_id in (None, "", "ALL", "all", "Todos") else dataset_id
    if ambito == "dataset" and not decision.get("pozos") and decision["intencion"] in ("estado", "medidas", "presiones", "caudal", "frecuencia", "comparar"):
        decision = {**decision, "pozos": pozos_de(dataset_filtro)}
    if ambito == "dataset" and decision["intencion"] == "comparar_contexto" and not (previo.get("pozos") or []):
        decision = {**decision, "intencion": "comparar", "pozos": pozos_de(dataset_filtro)}
    propio = cliente is None
    cfg = configuracion()
    if modelo:
        cfg = {**cfg, "modelo": modelo}
    if num_predict:
        cfg = {**cfg, "num_predict": num_predict}
    if propio:
        cliente = ClienteOllama(cfg["base_url"], min(cfg["timeout_s"], 45))
    try:
        return _responder(consulta, decision, previo, cliente, cfg, dataset_id, ambito, alcance)
    finally:
        if propio:
            cliente.cerrar()


def _responder(consulta, decision, previo, cliente, cfg, dataset_id=None, ambito=None, alcance=None) -> dict:
    alcance = alcance or {
        "dataset": "Todos" if dataset_id in (None, "", "ALL", "all", "Todos") else dataset_id,
        "pozo": "Todos" if ambito == "dataset" else ((decision.get("pozos") or [None])[0] or "Todos"),
    }
    intencion = decision["intencion"]
    if intencion == "fuera_de_alcance":
        mensaje = (
            "Puedo responder consultas sobre bombas electrosumergibles y los pozos de este expediente. "
            "Esa pregunta no entra en ese tema."
        )
        aviso = contrato_vacio(alcance=alcance, tipo="notice", titulo="Fuera de alcance", resumen=mensaje)
        aviso["answer"]["blocks"] = [{"type": "notice", "level": "info", "text": mensaje}]
        return _paquete(consulta, mensaje, True, None, [_FUENTE_PIP], previo, estructura=aviso, alcance=alcance)
    if intencion == "consulta_esp":
        return _consulta_esp(consulta, decision, previo, cliente, cfg, dataset_id, alcance)
    if intencion == "pozo_desconocido":
        mensaje = "No tengo ese pozo en el expediente que estoy consultando."
        aviso = contrato_vacio(alcance=alcance, tipo="notice", titulo="Pozo no encontrado", resumen=mensaje, status="error")
        aviso["answer"]["blocks"] = [{"type": "notice", "level": "error", "text": mensaje}]
        return _paquete(consulta, mensaje, False, None, [_FUENTE_MOTOR], previo, estructura=aviso, alcance=alcance)
    if intencion == "explicar_estado":
        return _explicar_estado_previo(consulta, decision, previo, cliente, cfg, dataset_id, ambito, alcance)
    if intencion == "seguimiento":
        bajo = consulta.lower()
        if any(giro in bajo for giro in ("presi", "pip", "thp")):
            decision = {**decision, "intencion": "presiones", "variable": "presiones"}
        elif any(giro in bajo for giro in ("caudal", "produce", "bfpd")):
            decision = {**decision, "intencion": "caudal", "variable": "caudal"}
        elif any(giro in bajo for giro in ("frecuen", "hz")):
            decision = {**decision, "intencion": "frecuencia", "variable": "frecuencia_hz"}
        elif any(giro in bajo for giro in ("significa", "estado", "resultado")):
            decision = {**decision, "intencion": "estado", "variable": "estado"}
        elif any(giro in bajo for giro in ("medida", "variable", "valor", "parámetro", "parametro")):
            decision = {**decision, "intencion": "medidas", "variable": "medidas"}
        else:
            decision = {**decision, "intencion": "estado", "variable": "estado"}
    elif intencion == "comparar_contexto":
        return _comparar_lo_ya_calculado(consulta, decision, previo, cliente, cfg, alcance)
    if intencion == "diferencia_pip":
        corrida = ejecutar({**decision, "intencion": "calcular"})
    else:
        corrida = ejecutar(decision)

    if not corrida["ok"]:
        respaldo = contrato_vacio(
            alcance=alcance,
            tipo="notice",
            titulo="Sin resultado consultable",
            resumen=corrida["error"],
            status="error",
        )
        respaldo["answer"]["blocks"] = [{"type": "notice", "level": "error", "text": corrida["error"]}]
        return _paquete(
            consulta, corrida["error"], False, None, [_FUENTE_MOTOR], previo,
            estructura=respaldo, alcance=alcance, linguistic_source="deterministic",
        )

    estructura, plantilla, fuentes = _respuesta_estructurada(decision, corrida, dataset_id, alcance)
    contrato = desde_estructura(estructura, alcance=alcance) if estructura else None
    if contrato is None and plantilla:
        tipo = "definition" if decision["intencion"] == "conceptual" else "open"
        contrato = contrato_vacio(alcance=alcance, tipo=tipo, titulo="", resumen=plantilla[:180])
        if tipo == "definition":
            contrato["answer"]["blocks"] = [{
                "type": "definition",
                "term": (decision.get("variable") or "concepto").upper(),
                "text": plantilla,
            }]
        else:
            contrato["answer"]["blocks"] = [{"type": "paragraph", "text": plantilla}]
    # Las respuestas «por qué» ya traen argumentación determinística; el LLM solo
    # añadía paráfrasis y duplicaba el cierre.
    variable = decision.get("variable") or ""
    omitir_llm = variable in ("motivo_estado", "motivo_caudal") or (
        estructura is not None and estructura.get("tipo") == "estado_pozo" and estructura.get("rotulo")
    )
    inferencia = None if omitir_llm else _explicar(cliente, cfg, plantilla, decision, contrato)
    filas = [completar(fila) for fila in corrida.get("filas") or []]
    if omitir_llm:
        visible = texto_contrato(contrato) if contrato else plantilla
        if contrato is not None:
            contrato["linguistic_source"] = "deterministic"
    else:
        contrato, visible, inferencia = _aplicar_linguistica(
            contrato, plantilla, inferencia, filas, decision,
        )
    nuevo = _contexto(previo, decision, corrida, ambito, dataset_id)
    return _paquete(
        consulta, visible, True, inferencia, fuentes, nuevo,
        estructura=contrato, alcance=alcance,
        linguistic_source=(contrato or {}).get("linguistic_source") or "deterministic",
    )


def _comparar_lo_ya_calculado(consulta, decision, previo, cliente, cfg, alcance=None) -> dict:
    guardados = previo.get("resultados") if isinstance(previo.get("resultados"), dict) else {}
    pozos = [pozo for pozo in (previo.get("pozos") or []) if pozo in guardados]
    if len(pozos) < 2:
        return _paquete(consulta, "Necesito al menos dos pozos ya consultados para decir cuál es mayor.", False, None, [_FUENTE_MOTOR], previo, alcance=alcance)
    filas = []
    for pozo in pozos[-2:]:
        dato = guardados[pozo]
        filas.append({
            "pozo": pozo,
            "pip_ft": dato.get("pip_ft"),
            "pip_visible": dato.get("pip_visible"),
            "thd_visible": dato.get("thd_visible"),
            "caudal_visible": dato.get("caudal_visible"),
        })
    corrida = {"ok": True, "filas": filas}
    decision = {**decision, "intencion": "comparar"}
    estructura, plantilla, fuentes = _respuesta_estructurada(decision, corrida, previo.get("dataset_id"), alcance or {})
    inferencia = _explicar(cliente, cfg, plantilla, decision)
    texto_modelo = inferencia.contenido if inferencia is not None else ""
    visible = _unir(plantilla, texto_modelo, plantilla)
    return _paquete(consulta, visible, True, inferencia, fuentes, _contexto(previo, decision, corrida), estructura=estructura, alcance=alcance)


def _explicar_estado_previo(consulta, decision, previo, cliente, cfg, dataset_id=None, ambito=None, alcance=None) -> dict:
    pozo = (decision.get("pozos") or [None])[0]
    if not pozo:
        return _paquete(
            consulta,
            "Selecciona un pozo para explicar su estado, o pregunta cómo están los pozos del dataset.",
            True,
            None,
            [_FUENTE_MOTOR],
            previo,
            alcance=alcance,
        )
    return _responder(consulta, {**decision, "intencion": "estado", "pozos": [pozo]}, previo, cliente, cfg, dataset_id, ambito, alcance)


def _consulta_esp(consulta, decision, previo, cliente, cfg, dataset_id=None, alcance=None) -> dict:
    dataset_filtro = None if dataset_id in (None, "", "ALL", "all", "Todos") else dataset_id
    alcance = alcance or {"dataset": "Todos", "pozo": "Todos"}
    estructura = estructurar("inventario", [], dataset_id=dataset_filtro, alcance=alcance)
    plantilla = texto_plano(estructura)
    contrato = desde_estructura(estructura, alcance=alcance)
    inferencia = _explicar(cliente, cfg, plantilla, decision, contrato)
    contrato, visible, inferencia = _aplicar_linguistica(
        contrato, plantilla, inferencia, [], decision,
    )
    return _paquete(
        consulta, visible, True, inferencia, [_FUENTE_MOTOR], previo,
        estructura=contrato, alcance=alcance,
        linguistic_source=(contrato or {}).get("linguistic_source"),
    )


def _respuesta_estructurada(decision: dict, corrida: dict, dataset_id: str | None, alcance: dict) -> tuple[dict | None, str, list[str]]:
    intencion = decision["intencion"]
    filas = corrida.get("filas") or []
    dataset_filtro = None if dataset_id in (None, "", "ALL", "all", "Todos") else dataset_id
    if intencion in ("estado", "medidas", "presiones", "caudal", "frecuencia", "inventario", "reglas"):
        tema = "estado" if intencion == "reglas" else intencion
        variable = decision.get("variable") or ""
        if variable == "motivo_estado" or (intencion == "estado" and variable == "estado" and len(filas) == 1):
            # Una sola pozo: respuesta con «por qué» y fórmulas comentadas.
            tema = "motivo_estado"
        if variable == "motivo_caudal" or (intencion == "caudal" and "motivo" in variable):
            tema = "motivo_caudal"
        estructura = estructurar(tema, filas, dataset_id=dataset_filtro, alcance=alcance or {})
        return estructura, texto_plano(estructura), list(estructura.get("fuentes") or [_FUENTE_MOTOR])
    plantilla, _, fuentes = _plantilla(decision, corrida, dataset_id)
    return None, plantilla, fuentes


def _plantilla(decision: dict, corrida: dict, dataset_id: str | None = None) -> tuple[str, list[str], list[str]]:
    intencion = decision["intencion"]
    filas = corrida["filas"]
    if intencion == "conceptual":
        if decision.get("variable") == "cavitacion":
            return (
                "La cavitación es la formación de burbujas de vapor cuando la presión del líquido baja hasta su presión de vapor. "
                "En una bomba electrosumergible interesa en la entrada, donde una presión demasiado baja puede dañar los impulsores. "
                "Esta explicación no calcula la presión de un pozo.",
                [],
                [_FUENTE_PIP],
            )
        return (
            f"{DEFINICION_PIP} En este expediente ese valor se expresa en pies de fluido, según la transcripción de la hoja, "
            "y la posición efectiva del sensor todavía no está confirmada.",
            [],
            [_FUENTE_PIP],
        )
    if intencion == "rechazar_autorizacion":
        return (
            "No puedo asegurar que cambiar la frecuencia sea seguro. Los límites usados en el análisis todavía requieren "
            "confirmación técnica y no autorizan una maniobra en el equipo real.",
            [],
            [_FUENTE_MOTOR],
        )
    if intencion == "aclarar":
        if decision.get("variable") == "eficiencia":
            return ("No tengo una eficiencia validada para ese pozo. No invento ese valor.", [], [_FUENTE_MOTOR])
        if decision.get("variable") == "no_autorizada":
            return ("Ese cambio no está entre las estimaciones disponibles. Puedo estimar una frecuencia o un caudal, sin modificar el pozo.", [], [_FUENTE_MOTOR])
        if decision.get("variable") == "pozo":
            return ("Para estimar ese cambio necesito saber de qué pozo se trata.", [], [_FUENTE_MOTOR])
        if decision.get("variable") == "frecuencia_hz":
            return ("Para estimar ese cambio necesito la frecuencia, en hertz, o el caudal, en BFPD, y el pozo.", [], [_FUENTE_MOTOR])
        return ("Necesito un poco más de precisión: el pozo y qué valor quieres conocer.", [], [_FUENTE_MOTOR])
    if intencion == "inventario":
        return redactar("inventario", [], dataset_id), [], [_FUENTE_MOTOR]
    if not filas:
        return ("No tengo un cálculo previo para comparar. Indica los pozos.", [], [_FUENTE_MOTOR])
    cifras = _cifras(filas)
    if intencion == "comparar":
        return _comparar(filas), cifras, [_FUENTE_MOTOR]
    fila = filas[0]
    if intencion in ("estado", "medidas", "presiones", "caudal", "frecuencia"):
        texto = redactar(intencion, filas, dataset_id)
        return texto, _cifras_magnitudes(filas) or cifras, [_FUENTE_MOTOR]
    if intencion == "reglas":
        return _reglas(fila), cifras, [_FUENTE_MOTOR]
    if intencion == "simular":
        return _simulacion(fila, decision.get("cambios") or {}), cifras, [_FUENTE_MOTOR]
    if intencion == "diferencia_pip":
        return _diferencia(fila), cifras, [_FUENTE_MOTOR, _FUENTE_PIP]
    return _calculo(fila, decision.get("variable") or "pip_ft"), cifras, [_FUENTE_MOTOR, _FUENTE_PIP]


def _calculo(fila: dict, variable: str) -> str:
    if variable == "thd_total_ft":
        return (
            f"La altura total de descarga calculada para {fila['pozo']} es {fila['thd_visible']} ft. "
            "Sale del balance de la hoja. No es una orden de operar la bomba."
        )
    if variable == "caudal_operacion_bfpd":
        return (
            f"El caudal de intersección calculado para {fila['pozo']} es {fila['caudal_visible']} BFPD. "
            "Es el punto en que la curva, llevada a la frecuencia de la hoja, iguala la altura total. "
            "No es el caudal registrado."
        )
    return (
        f"La presión de admisión calculada para {fila['pozo']} es {fila['pip_visible']} ft. "
        "Es el valor transcrito de la hoja. La posición en la que el sensor mide, y el signo frente a la "
        "columna hidrostática, todavía no están confirmados, así que este número no cierra esa duda."
    )


def _reglas(fila: dict) -> str:
    return redactar("estado", [fila])


def _simulacion(fila: dict, cambios: dict) -> str:
    detalle = []
    if "frecuencia_hz" in cambios:
        detalle.append(f"{formato_visible(cambios['frecuencia_hz'])} Hz")
    if "caudal_operacion_bfpd" in cambios:
        detalle.append(f"{formato_visible(cambios['caudal_operacion_bfpd'])} BFPD")
    cambio = " y ".join(detalle) or "el cambio indicado"
    nota = " Esa frecuencia no está entre las medidas de las hojas." if fila.get("fuera_de_lo_observado") else ""
    return (
        f"Si en {fila['pozo']} se usara {cambio}, el cálculo de la hoja daría una presión de admisión de "
        f"{fila['pip_visible']} ft, una altura total de {fila['thd_visible']} ft y un caudal de intersección de "
        f"{fila['caudal_visible']} BFPD. {_significado_estado(fila)} "
        f"Es una estimación con las hipótesis del modelo, no un cambio en el pozo "
        f"ni una instrucción para mover el equipo.{nota}"
    )


def _significado_estado(fila: dict) -> str:
    reglas = set(fila.get("reglas") or [])
    if "RC-BES-02" in reglas:
        hecho = "el caudal queda bajo el mínimo escrito a esta frecuencia"
    elif "RC-BES-01" in reglas:
        hecho = "el caudal supera el máximo escrito a esta frecuencia"
    elif fila.get("estado") == "NORMAL":
        hecho = "el caudal queda entre el mínimo y el máximo escritos a esta frecuencia"
    else:
        hecho = "no hay una clasificación de caudal para este punto"
    rotulo = str(fila.get("rotulo") or "sin clasificación").lower()
    return (
        f"El estado es {rotulo}: {hecho}. "
        "Ese resultado no autoriza una maniobra ni asegura que la operación sea segura."
    )


def _diferencia(fila: dict) -> str:
    return (
        f"La presión de admisión que devuelve la hoja para {fila['pozo']} es {fila['pip_visible']} ft. "
        "Una corrección hidrostática distinta cambiaría ese número según dónde se considere que mide el sensor. "
        "Esa posición no está confirmada. El valor de la hoja se conserva; no hay evidencia aquí para declarar que la fórmula original esté equivocada."
    )


def _comparar(filas: list[dict]) -> str:
    lineas = [
        f"{fila['pozo']}: admisión {fila['pip_visible']} ft, altura total {fila['thd_visible']} ft, caudal de intersección {fila['caudal_visible']} BFPD."
        for fila in filas
    ]
    orden = sorted(filas, key=lambda fila: fila["pip_ft"] if isinstance(fila["pip_ft"], (int, float)) else -1, reverse=True)
    mayor = orden[0]["pozo"] if orden and isinstance(orden[0]["pip_ft"], (int, float)) else ""
    cierre = f" La mayor presión de admisión, en pies de fluido, es la de {mayor}." if mayor else ""
    return " ".join(lineas) + cierre + " La comparación usa el cálculo de cada hoja y no autoriza una maniobra."


def _cifras(filas: list[dict]) -> list[str]:
    cifras = []
    for fila in filas:
        for clave in ("pip_visible", "thd_visible", "caudal_visible"):
            if fila.get(clave):
                cifras.append(str(fila[clave]))
    return cifras


_SISTEMA = (
    "Eres el asistente técnico de HUC para pozos con bomba electrosumergible.\n"
    "Tu rol: explicar hechos ya calculados. No calculas ni inventas cifras, unidades ni estados.\n"
    "Responde en español profesional, natural y preciso.\n"
    "Devuelve solo JSON con las claves resumen y explicacion.\n"
    "resumen: una o dos frases. explicacion: desarrollo breve sin repetir el resumen.\n"
    "Conserva todos los números y unidades del texto de hechos exactamente.\n"
    "No autorices maniobras. No menciones códigos internos, contratos ni nombres de funciones."
)


def _explicar(cliente, cfg, plantilla: str, decision: dict, contrato: dict | None = None):
    if decision["intencion"] in ("rechazar_autorizacion", "aclarar", "fuera_de_alcance"):
        return None
    contexto = ""
    if contrato:
        ctx = contrato.get("context") or {}
        contexto = f"Contexto: dataset={ctx.get('dataset_id')}; pozo={ctx.get('well_id') or 'Todos'}.\n"
    mensajes = [
        {"role": "system", "content": _SISTEMA},
        {
            "role": "user",
            "content": (
                f"{contexto}Hechos verificados (no los alteres):\n{plantilla}\n\n"
                "Redacta resumen y explicacion en JSON."
            ),
        },
    ]
    try:
        inferencia = cliente.consultar(
            cfg["modelo"],
            mensajes,
            min(int(cfg["num_predict"]), 320),
            temperature=0,
            formato="json",
        )
    except Exception:
        return None
    if not getattr(inferencia, "ok", False) or getattr(inferencia, "incompleta", False):
        return None
    return inferencia


def _aplicar_linguistica(contrato, plantilla, inferencia, filas, decision):
    rotulos = [fila.get("rotulo") or "" for fila in filas]
    pozos = [fila.get("pozo") or "" for fila in filas]
    base_corpus = corpus(filas, plantilla)
    if contrato is None:
        visible = plantilla
        if inferencia is not None:
            visible = _unir(plantilla, inferencia.contenido, base_corpus, rotulos, pozos)
        return None, visible, inferencia

    aporte = _parsear_aporte(getattr(inferencia, "contenido", "") if inferencia else "")
    if aporte:
        candidato = fusionar_linguistica(contrato, aporte)
        texto_prueba = " ".join([
            candidato["answer"].get("summary") or "",
            " ".join(
                b.get("text") or ""
                for b in candidato["answer"].get("blocks") or []
                if b.get("role") == "model"
            ),
        ])
        if _aporte_valido(texto_prueba, _cifras_de_texto(base_corpus)) and elegir(plantilla, texto_prueba, base_corpus, rotulos, pozos) != plantilla:
            ok, _ = validar_contrato(candidato)
            if ok:
                return candidato, texto_contrato(candidato), inferencia
        # Si el JSON trae cifras inventadas, se conserva el contrato determinístico.
    elif inferencia is not None and inferencia.contenido:
        # Compatibilidad: texto libre del modelo como explicación.
        unido = _unir(plantilla, inferencia.contenido, base_corpus, rotulos, pozos)
        if unido != plantilla:
            contrato = fusionar_linguistica(contrato, {"resumen": contrato["answer"].get("summary") or "", "explicacion": unido})
    ok, _ = validar_contrato(contrato)
    if not ok:
        contrato = desde_estructura(
            {"titulo": "Respuesta", "resumen": plantilla, "secciones": [], "explicacion": "", "tipo": "vacio", "fuentes": []},
            alcance=contrato.get("context") and {
                "dataset": (contrato.get("context") or {}).get("dataset_id") or "Todos",
                "pozo": (contrato.get("context") or {}).get("well_id") or "Todos",
            } or {},
        )
        contrato["answer"]["blocks"] = [{"type": "notice", "level": "info", "text": plantilla}]
        contrato["linguistic_source"] = "deterministic"
    return contrato, texto_contrato(contrato) or plantilla, inferencia


def _parsear_aporte(texto: str) -> dict | None:
    if not texto or not texto.strip():
        return None
    try:
        doc = json.loads(texto)
    except json.JSONDecodeError:
        inicio = texto.find("{")
        fin = texto.rfind("}")
        if inicio < 0 or fin <= inicio:
            return None
        try:
            doc = json.loads(texto[inicio:fin + 1])
        except json.JSONDecodeError:
            return None
    if not isinstance(doc, dict):
        return None
    return {
        "resumen": str(doc.get("resumen") or doc.get("summary") or "").strip(),
        "explicacion": str(doc.get("explicacion") or doc.get("explanation") or "").strip(),
    }


def _unir(plantilla: str, texto: str, corpus_texto, rotulos: list[str] | None = None, pozos: list[str] | None = None) -> str:
    if isinstance(corpus_texto, list):
        corpus_texto = plantilla + " " + " ".join(str(item) for item in corpus_texto)
    if not _aporte_valido(texto, _cifras_de_texto(corpus_texto)):
        return plantilla
    return elegir(plantilla, texto, corpus_texto, rotulos or [], pozos or [])


def _cifras_de_texto(texto: str) -> list[str]:
    return re.findall(r"\d+\.\d+", texto or "")


def _cifras_magnitudes(filas: list[dict]) -> list[str]:
    cifras = []
    for fila in filas:
        for item in fila.get("magnitudes") or []:
            if item.get("visible"):
                cifras.append(str(item["visible"]))
    return cifras


def _aporte_valido(texto: str, cifras: list[str]) -> bool:
    if not texto or not texto.strip() or not re.search(r"[A-Za-zÁÉÍÓÚáéíóúñÑ]", texto):
        return False
    if re.search(r"sin riesgo|puedes aumentar|puede aumentar|está segura|esta segura|autorizo|RC-BES|CT-0\d|contrato|evaluar_|ollama|traceback|d[oó]lar|bitcoin", texto, re.IGNORECASE):
        return False
    if cifras and re.search(r"pump intake pressure|presión del fluido en la entrada", texto, re.IGNORECASE):
        return False
    permitidas = set(cifras)
    return all(hallada in permitidas for hallada in _CIFRA.findall(texto))


def _contexto(previo: dict, decision: dict, corrida: dict, ambito: str | None = None, dataset_id: str | None = None) -> dict:
    filas = corrida.get("filas") or []
    acumulados = [pozo for pozo in (previo.get("pozos") or []) if isinstance(pozo, str)]
    for fila in filas:
        if fila.get("pozo") and fila["pozo"] not in acumulados:
            acumulados.append(fila["pozo"])
    guardados = dict(previo.get("resultados") or {})
    for fila in filas:
        if "pip_ft" not in fila:
            continue
        guardados[fila["pozo"]] = {
            "pip_visible": fila.get("pip_visible"),
            "thd_visible": fila.get("thd_visible"),
            "caudal_visible": fila.get("caudal_visible"),
            "pip_ft": fila.get("pip_ft"),
            "estado": fila.get("estado"),
            "rotulo": fila.get("rotulo"),
            "reglas": list(fila.get("reglas") or []),
        }
    return {
        "pozo": None if ambito == "dataset" else (acumulados[-1] if acumulados else None),
        "pozos": acumulados,
        "variable": decision.get("variable") or previo.get("variable") or "",
        "resultados": guardados,
        "dataset_id": dataset_id or previo.get("dataset_id") or "",
        "ambito": ambito or previo.get("ambito") or "",
    }


def _paquete(consulta, contenido, ok, inferencia, fuentes, contexto, estructura=None, alcance=None, linguistic_source: str | None = None) -> dict:
    alcance = alcance or {}
    if isinstance(estructura, dict) and estructura.get("schema_version") != "1.0" and estructura.get("secciones") is not None:
        estructura = desde_estructura(estructura, alcance=alcance)
    if isinstance(estructura, dict) and linguistic_source:
        estructura = {**estructura, "linguistic_source": linguistic_source}
    return {
        "contexto": contexto,
        "inferencia": {
            "ok": ok,
            "contenido": contenido,
            "error": "" if ok else contenido,
            "incompleta": bool(getattr(inferencia, "incompleta", False)),
            "modelo": getattr(inferencia, "modelo", "") or "",
            "done_reason": getattr(inferencia, "done_reason", "") or "",
            "duracion_s": getattr(inferencia, "duracion_s", None),
            "tokens_generados": getattr(inferencia, "tokens_generados", None),
            "thinking_descartado": bool(getattr(inferencia, "thinking_descartado", False)),
            "consulta": (consulta or "")[:500],
            "fuentes": fuentes,
            "pozo": alcance.get("pozo") or contexto.get("pozo"),
            "dataset": alcance.get("dataset") or contexto.get("dataset_id") or "",
            "ambito": contexto.get("ambito") or "",
            "alcance": alcance,
            "estructura": estructura,
            "etiqueta": etiqueta_alcance(alcance) if alcance else "",
            "linguistic_source": (estructura or {}).get("linguistic_source") if isinstance(estructura, dict) else (linguistic_source or "deterministic"),
        },
    }
