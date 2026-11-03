"""Contrato de presentación asistente ↔ Django. Los números no los inventa el modelo."""

from __future__ import annotations

from html import escape
from typing import Any
from uuid import uuid4

SCHEMA_VERSION = "1.0"
BLOQUES = frozenset({
    "paragraph", "metrics", "table", "list", "status", "comparison", "definition", "notice",
})
TIPOS_RESPUESTA = frozenset({
    "well_status", "wells_summary", "metrics", "pressures", "flow", "frequency",
    "inventory", "definition", "comparison", "notice", "open", "fallback",
})


def nuevo_id() -> str:
    return uuid4().hex[:12]


def contrato_vacio(*, alcance: dict, tipo: str = "notice", titulo: str = "", resumen: str = "", status: str = "ok") -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "response_id": nuevo_id(),
        "context": {
            "dataset_id": _dataset(alcance),
            "well_id": _pozo(alcance),
            "scenario_id": None,
        },
        "answer": {
            "type": tipo if tipo in TIPOS_RESPUESTA else "notice",
            "title": titulo,
            "summary": resumen,
            "blocks": [],
        },
        "references": [],
        "status": status,
        "linguistic_source": "deterministic",
    }


def desde_estructura(estructura: dict | None, *, alcance: dict, tipo: str | None = None) -> dict:
    """Convierte la estructura determinística actual al contrato versionado."""
    estructura = estructura if isinstance(estructura, dict) else {}
    tipo_respuesta = tipo or _tipo_desde(estructura.get("tipo") or "")
    contrato = contrato_vacio(
        alcance=alcance or estructura.get("alcance") or {},
        tipo=tipo_respuesta,
        titulo=str(estructura.get("titulo") or ""),
        resumen=str(estructura.get("resumen") or ""),
        status="ok" if estructura else "fallback",
    )
    bloques: list[dict] = []
    for seccion in estructura.get("secciones") or []:
        if not isinstance(seccion, dict):
            continue
        titulo = str(seccion.get("titulo") or "").strip()
        for parrafo in seccion.get("parrafos") or []:
            texto = str(parrafo).strip()
            if texto:
                bloques.append({"type": "paragraph", "text": texto, "heading": titulo or None})
                titulo = ""
        tabla = seccion.get("tabla")
        if isinstance(tabla, dict) and tabla.get("filas"):
            bloques.append({
                "type": "table",
                "heading": titulo or None,
                "columns": [str(c) for c in (tabla.get("columnas") or [])],
                "rows": [[str(c) for c in fila] for fila in (tabla.get("filas") or [])],
            })
            titulo = ""
        lista = seccion.get("lista") or []
        if lista:
            bloques.append({
                "type": "list",
                "heading": titulo or None,
                "items": [str(item) for item in lista],
            })
    if estructura.get("explicacion"):
        bloques.append({"type": "paragraph", "text": str(estructura["explicacion"]), "heading": None})
    if estructura.get("tipo") == "estado_pozo":
        # Preferir el rótulo del resultado; no buscarlo en el texto (evita confundir
        # «NORMAL» citado como ejemplo dentro de una explicación de REGISTRO).
        rotulo = str(estructura.get("rotulo") or "").strip().upper().replace("CRITICO", "CRÍTICO")
        if not rotulo:
            rotulo = _extraer_estado(estructura.get("titulo") or "")
        if rotulo in ("NORMAL", "REGISTRO", "CRÍTICO", "INCIPIENTE"):
            bloques.insert(0, {
                "type": "status",
                "label": rotulo,
                "text": f"Estado calculado: {rotulo}.",
            })
    # La explicación larga ya va en secciones; no duplicar el cierre suelto.
    contrato["answer"]["blocks"] = bloques
    contrato["references"] = list(estructura.get("fuentes") or [])
    return contrato


def fusionar_linguistica(contrato: dict, aporte: dict | None) -> dict:
    """Integra solo campos lingüísticos validados. No toca tablas ni métricas.

    Evita repeticiones: el resumen del modelo sustituye al determinístico; la
    explicación solo se agrega si aporta contenido nuevo frente a resumen/tabla.
    """
    from services.chat_dedupe import aporta_novedad, dedupe_frases

    if not isinstance(contrato, dict):
        return contrato_vacio(alcance={}, status="fallback")
    salida = {
        **contrato,
        "answer": {**(contrato.get("answer") or {}), "blocks": list((contrato.get("answer") or {}).get("blocks") or [])},
    }
    if not isinstance(aporte, dict):
        return _dedupe_contrato(salida)
    resumen = dedupe_frases(str(aporte.get("resumen") or "").strip())
    explicacion = dedupe_frases(str(aporte.get("explicacion") or "").strip())
    bases = []
    if resumen:
        salida["answer"]["summary"] = resumen
        bases.append(resumen)
    else:
        bases.append(str(salida["answer"].get("summary") or ""))
    # Texto ya presente en bloques determinísticos (párrafos/tablas).
    for bloque in salida["answer"]["blocks"]:
        if bloque.get("type") == "paragraph" and bloque.get("text"):
            bases.append(str(bloque["text"]))
        if bloque.get("type") == "table":
            for fila in bloque.get("rows") or []:
                bases.append(" ".join(str(c) for c in fila))
    # Quitar párrafos determinísticos que solo reiteran el nuevo resumen.
    if resumen:
        depurados = []
        for bloque in salida["answer"]["blocks"]:
            if bloque.get("type") == "paragraph" and bloque.get("role") != "model":
                if not aporta_novedad(str(bloque.get("text") or ""), [resumen], umbral=0.72):
                    continue
            if bloque.get("type") == "paragraph" and bloque.get("role") == "model":
                continue
            depurados.append(bloque)
        salida["answer"]["blocks"] = depurados
    especulativa = any(
        giro in explicacion.casefold()
        for giro in (
            "podría reflejar", "podria reflejar", "sugiere que", "sugiere un", "lo que sugiere",
            "probablemente", "posible daño", "saturación", "saturacion", "yacimiento", "reservorio",
            "riesgo de", "conviene subir", "conviene bajar", "dominado por agua",
        )
    )
    if explicacion and not especulativa and aporta_novedad(explicacion, bases, umbral=0.75):
        bloques = [b for b in salida["answer"]["blocks"] if not (b.get("type") == "paragraph" and b.get("role") == "model")]
        bloques.append({"type": "paragraph", "text": explicacion, "heading": None, "role": "model"})
        salida["answer"]["blocks"] = bloques
        salida["linguistic_source"] = "model"
    elif resumen:
        salida["linguistic_source"] = "model"
    return _dedupe_contrato(salida)


def _dedupe_contrato(contrato: dict) -> dict:
    from services.chat_dedupe import aporta_novedad, dedupe_frases

    answer = contrato.get("answer") or {}
    resumen = dedupe_frases(str(answer.get("summary") or ""))
    answer["summary"] = resumen
    vistos = [resumen] if resumen else []
    bloques = []
    for bloque in answer.get("blocks") or []:
        if bloque.get("type") == "paragraph":
            texto = dedupe_frases(str(bloque.get("text") or ""))
            if not texto or not aporta_novedad(texto, vistos, umbral=0.8):
                continue
            bloque = {**bloque, "text": texto}
            vistos.append(texto)
        bloques.append(bloque)
    answer["blocks"] = bloques
    contrato["answer"] = answer
    return contrato


def validar(contrato: Any) -> tuple[bool, str]:
    if not isinstance(contrato, dict):
        return False, "contrato_no_objeto"
    if contrato.get("schema_version") != SCHEMA_VERSION:
        return False, "schema_version"
    answer = contrato.get("answer")
    if not isinstance(answer, dict):
        return False, "answer"
    if answer.get("type") not in TIPOS_RESPUESTA:
        return False, "answer.type"
    if not isinstance(answer.get("blocks"), list):
        return False, "blocks"
    for bloque in answer["blocks"]:
        if not isinstance(bloque, dict) or bloque.get("type") not in BLOQUES:
            return False, f"bloque:{bloque.get('type') if isinstance(bloque, dict) else type(bloque)}"
        ok, motivo = _validar_bloque(bloque)
        if not ok:
            return False, motivo
    contexto = contrato.get("context")
    if not isinstance(contexto, dict):
        return False, "context"
    return True, ""


def render_html(contrato: dict) -> str:
    """HTML escapado a partir del contrato. Django decide la presentación."""
    ok, _ = validar(contrato)
    if not ok:
        fallo = contrato_vacio(
            alcance={},
            tipo="notice",
            titulo="Respuesta no disponible",
            resumen="La estructura de respuesta no pasó la validación.",
            status="error",
        )
        fallo["answer"]["blocks"] = [{
            "type": "notice",
            "level": "error",
            "text": "La estructura de respuesta no pasó la validación.",
        }]
        return render_html(fallo)
    answer = contrato["answer"]
    partes = ['<div class="asistente-estructura" data-schema="1.0">']
    if answer.get("title"):
        partes.append(f'<h3 class="asistente-titulo">{escape(str(answer["title"]))}</h3>')
    if answer.get("summary"):
        partes.append(f'<p class="asistente-resumen">{escape(str(answer["summary"]))}</p>')
    for bloque in answer.get("blocks") or []:
        partes.append(_html_bloque(bloque))
    partes.append("</div>")
    return "".join(partes)


def texto_plano(contrato: dict) -> str:
    ok, _ = validar(contrato)
    if not ok:
        return ""
    answer = contrato["answer"]
    partes = []
    if answer.get("title"):
        partes.append(str(answer["title"]))
    if answer.get("summary"):
        partes.append(str(answer["summary"]))
    for bloque in answer.get("blocks") or []:
        tipo = bloque.get("type")
        if bloque.get("heading"):
            partes.append(str(bloque["heading"]))
        if tipo == "paragraph":
            partes.append(str(bloque.get("text") or ""))
        elif tipo == "definition":
            partes.append(f"{bloque.get('term')}: {bloque.get('text')}")
        elif tipo == "notice":
            partes.append(str(bloque.get("text") or ""))
        elif tipo == "status":
            partes.append(str(bloque.get("text") or bloque.get("label") or ""))
        elif tipo == "list":
            for item in bloque.get("items") or []:
                partes.append(f"- {item}")
        elif tipo == "metrics":
            for item in bloque.get("items") or []:
                partes.append(f"{item.get('name')}: {item.get('value')} {item.get('unit') or ''}".strip())
        elif tipo == "table":
            partes.append(" | ".join(str(c) for c in (bloque.get("columns") or [])))
            for fila in bloque.get("rows") or []:
                partes.append(" | ".join(str(c) for c in fila))
        elif tipo == "comparison":
            partes.append(str(bloque.get("text") or ""))
    return "\n\n".join(p for p in partes if p)


def _validar_bloque(bloque: dict) -> tuple[bool, str]:
    tipo = bloque["type"]
    if tipo == "paragraph":
        return (isinstance(bloque.get("text"), str) and bool(bloque["text"].strip())), "paragraph.text"
    if tipo == "definition":
        return bool(str(bloque.get("term") or "").strip() and str(bloque.get("text") or "").strip()), "definition"
    if tipo == "notice":
        return bool(str(bloque.get("text") or "").strip()), "notice"
    if tipo == "status":
        return bool(str(bloque.get("label") or "").strip()), "status"
    if tipo == "list":
        return isinstance(bloque.get("items"), list), "list"
    if tipo == "metrics":
        items = bloque.get("items")
        if not isinstance(items, list):
            return False, "metrics"
        for item in items:
            if not isinstance(item, dict) or "name" not in item or "value" not in item:
                return False, "metrics.item"
        return True, ""
    if tipo == "table":
        return isinstance(bloque.get("columns"), list) and isinstance(bloque.get("rows"), list), "table"
    if tipo == "comparison":
        return True, ""
    return False, "tipo"


def _html_bloque(bloque: dict) -> str:
    tipo = bloque.get("type")
    heading = bloque.get("heading")
    prefijo = f"<h4>{escape(str(heading))}</h4>" if heading else ""
    if tipo == "paragraph":
        return f'<section class="asistente-seccion">{prefijo}<p>{escape(str(bloque.get("text") or ""))}</p></section>'
    if tipo == "definition":
        return (
            f'<section class="asistente-seccion asistente-definicion">{prefijo}'
            f'<p><strong>{escape(str(bloque.get("term") or ""))}</strong>. {escape(str(bloque.get("text") or ""))}</p></section>'
        )
    if tipo == "notice":
        nivel = escape(str(bloque.get("level") or "info"))
        return f'<p class="asistente-aviso asistente-aviso-{nivel}">{escape(str(bloque.get("text") or ""))}</p>'
    if tipo == "status":
        label = escape(str(bloque.get("label") or ""))
        texto = str(bloque.get("text") or "").strip()
        cuerpo = f"<p>{escape(texto)}</p>" if texto else ""
        return (
            f'<section class="asistente-seccion asistente-estado">'
            f'<span class="asistente-estado-rotulo" data-estado="{label}">{label}</span>'
            f"{cuerpo}</section>"
        )
    if tipo == "list":
        items = "".join(f"<li>{escape(str(i))}</li>" for i in (bloque.get("items") or []))
        return f'<section class="asistente-seccion">{prefijo}<ul>{items}</ul></section>'
    if tipo == "metrics":
        filas = []
        for item in bloque.get("items") or []:
            valor = escape(str(item.get("value") or "—"))
            unidad = escape(str(item.get("unit") or ""))
            nombre = escape(str(item.get("name") or item.get("id") or ""))
            filas.append(f"<tr><td>{nombre}</td><td class=\"asistente-valor\">{valor} {unidad}</td></tr>")
        return (
            f'<section class="asistente-seccion">{prefijo}'
            f'<div class="asistente-tabla-wrap"><table class="asistente-tabla asistente-metricas">'
            f"<thead><tr><th>Magnitud</th><th>Valor</th></tr></thead><tbody>{''.join(filas)}</tbody></table></div></section>"
        )
    if tipo == "table":
        cols = bloque.get("columns") or []
        thead = "<thead><tr>" + "".join(f"<th>{escape(str(c))}</th>" for c in cols) + "</tr></thead>" if cols else ""
        body = []
        for fila in bloque.get("rows") or []:
            body.append("<tr>" + "".join(f"<td>{escape(str(c))}</td>" for c in fila) + "</tr>")
        return (
            f'<section class="asistente-seccion">{prefijo}'
            f'<div class="asistente-tabla-wrap"><table class="asistente-tabla">{thead}'
            f"<tbody>{''.join(body)}</tbody></table></div></section>"
        )
    if tipo == "comparison":
        return f'<section class="asistente-seccion">{prefijo}<p>{escape(str(bloque.get("text") or ""))}</p></section>'
    return ""


def _dataset(alcance: dict) -> str:
    valor = str((alcance or {}).get("dataset") or "Todos")
    return "ALL" if valor in ("Todos", "ALL", "all", "") else valor


def _pozo(alcance: dict) -> str | None:
    valor = str((alcance or {}).get("pozo") or "Todos")
    if valor in ("Todos", "ALL", "all", ""):
        return None
    return valor


def _tipo_desde(tipo_interno: str) -> str:
    mapa = {
        "estado_pozo": "well_status",
        "estado_general": "wells_summary",
        "medidas_pozo": "metrics",
        "medidas_general": "metrics",
        "presiones": "pressures",
        "caudal": "flow",
        "frecuencia": "frequency",
        "inventario": "inventory",
        "vacio": "notice",
    }
    return mapa.get(tipo_interno, "open")


def _extraer_estado(texto: str) -> str:
    """Solo patrones «está en X» / «Por qué … en X». No busca la palabra suelta."""
    import re

    limpio = (texto or "").upper().replace("Í", "I")
    hallado = re.search(
        r"(?:ESTA|ESTÁ|EN)\s+(REGISTRO|NORMAL|CRITICO|CRÍTICO|INCIPIENTE)\b",
        limpio,
    )
    if not hallado:
        hallado = re.search(
            r"POR QUE\s+\S+\s+ESTA\s+EN\s+(REGISTRO|NORMAL|CRITICO|CRÍTICO|INCIPIENTE)\b",
            limpio,
        )
    if not hallado:
        return ""
    valor = hallado.group(1).replace("CRITICO", "CRÍTICO")
    return "CRÍTICO" if valor in ("CRITICO", "CRÍTICO") else valor
