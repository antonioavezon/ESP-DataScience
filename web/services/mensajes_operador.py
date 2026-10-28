"""Texto de la pantalla. El estado lo fija el motor; Ollama solo puede explicarlo."""

from __future__ import annotations

import json
import re

from services.ollama_client import ClienteOllama, configuracion

_CONTRADICCION = re.compile(
    r"correcto|segura|seguro|sin riesgo|puede operar|aplique este cambio|está bien|esta bien",
    re.IGNORECASE,
)


def mensaje_deterministico(clasificacion: dict, salida: dict, modificadas: list[str]) -> dict:
    codigo = clasificacion["codigo"]
    reglas = {regla.get("id"): regla for regla in salida.get("reglas") or [] if isinstance(regla, dict)}
    if codigo == "ERROR_CALCULO":
        detalle = _primer_error(salida)
        return _paquete(
            "No fue posible completar el cálculo.",
            "Este aviso no es un estado de la bomba. Revise el dato rechazado.",
            detalle,
        )
    if codigo == "SIN_DATOS":
        if clasificacion.get("rotulo") == "REGISTRO":
            return _paquete(
                "Hay un resultado calculado. Este expediente no clasifica el punto con una regla de caudal.",
                "",
                "",
            )
        return _paquete(
            "Evaluación no disponible: faltan datos.",
            "La falta de datos no es una condición crítica ni incipiente.",
            "",
        )
    if codigo == "CRITICO":
        return _paquete(
            "Una regla aprobada y marcada como límite crítico validado está activa en este escenario.",
            "No aplique este cambio a la bomba real. Confirme la regla antes de cualquier acción en campo.",
            "",
        )
    if codigo == "NORMAL":
        return _paquete(
            "El caudal está entre el mínimo y el máximo escritos a esta frecuencia.",
            "",
            "",
        )
    if codigo == "INCIPIENTE":
        activa = next((reglas[nombre] for nombre in ("RC-BES-01", "RC-BES-02") if reglas.get(nombre, {}).get("activada")), None)
        if activa and activa.get("id") == "RC-BES-02":
            mensaje = "El caudal queda bajo el mínimo escrito a esta frecuencia."
        else:
            mensaje = "El caudal supera el máximo escrito a esta frecuencia."
        return _paquete(mensaje, "", "")
    return _paquete(
        "Evaluación no disponible: faltan datos.",
        "",
        "",
    )


def _lista_valores(valores: dict) -> str:
    partes = []
    for clave, item in (valores or {}).items():
        if isinstance(item, dict):
            if item.get("valor") is None:
                continue
            nombre = item.get("nombre") or clave
            visible = item.get("valor_visible")
            if visible is None:
                visible = item.get("valor")
            unidad = item.get("unidad") or ""
            partes.append(f"{nombre} {visible} {unidad}".strip())
        elif item is not None:
            partes.append(f"{clave} {item}")
    return "; ".join(partes) or "ninguno"


def explicar(clasificacion: dict, respaldo: dict, modificadas: list[str], valores: dict) -> dict:
    """Pide una explicación. Si contradice el estado, se queda el texto determinístico."""
    cfg = configuracion()
    cliente = ClienteOllama(cfg["base_url"], min(cfg["timeout_s"], 45))
    consulta = (
        f"Rótulo ya decidido por el motor: {clasificacion['rotulo']}. "
        f"Reglas activas: {', '.join(clasificacion.get('reglas') or []) or 'ninguna'}. "
        "Conserva ese rótulo. No uses ningún otro rótulo. "
        "No inventes números ni umbrales. No reinterpretas códigos internos. "
        "No afirmes riesgos, consecuencias ni maniobras que no estén en el mensaje de respaldo. "
        "Explica en dos frases el mensaje de respaldo.\n"
        f"Mensaje de respaldo: {respaldo['mensaje']}\n"
        f"Variables modificadas: {', '.join(modificadas) or 'ninguna'}.\n"
        f"Valores publicados: {_lista_valores(valores)}."
        + (
            " Cita esos valores con su unidad. No calcules magnitudes que no estén en la lista."
            if clasificacion.get("rotulo") == "REGISTRO" or clasificacion.get("codigo") == "SIN_DATOS"
            else ""
        )
    )
    try:
        inferencia = cliente.consultar(
            cfg["modelo"],
            [
                {"role": "system", "content": "Eres un redactor de la consola ESP. No cambias el estado calculado. No revelas razonamiento interno."},
                {"role": "user", "content": consulta},
            ],
            min(180, cfg["num_predict"]),
        )
    finally:
        cliente.cerrar()
    if (
        not inferencia.ok
        or inferencia.incompleta
        or not _compatible(inferencia.contenido, clasificacion)
        or _trae_cifra_nueva(inferencia.contenido, clasificacion, respaldo, valores)
    ):
        return {**respaldo, "origen": "deterministico", "modelo_usado": False}
    return {
        "mensaje": inferencia.contenido,
        "accion": respaldo["accion"],
        "nota": respaldo["nota"],
        "origen": "ollama",
        "modelo_usado": True,
    }


def _trae_cifra_nueva(texto: str, clasificacion: dict, respaldo: dict, valores: dict) -> bool:
    permitidas = json.dumps(
        {"clasificacion": clasificacion, "respaldo": respaldo, "valores": valores},
        ensure_ascii=False,
    )
    for hallazgo in re.finditer(r"\d+(?:[.,]\d+)?", texto or ""):
        cifra = hallazgo.group(0)
        if cifra not in permitidas and cifra.replace(",", ".") not in permitidas:
            return True
    return False


def _compatible(texto: str, clasificacion: dict) -> bool:
    if isinstance(clasificacion, str):
        clasificacion = {"codigo": clasificacion, "condicion": ""}
    if not texto or not texto.strip():
        return False
    if re.search(r"segura|seguro|sin riesgo|puede operar|autoriz", texto, re.IGNORECASE):
        return False
    codigo = clasificacion.get("codigo")
    if codigo != "NORMAL" and (_CONTRADICCION.search(texto) or re.search(r"\bnormal\b", texto, re.IGNORECASE)):
        return False
    if codigo != "CRITICO" and re.search(r"\bcr[ií]tic[oa]\b", texto, re.IGNORECASE):
        return False
    if codigo != "INCIPIENTE" and re.search(r"\bincipiente\b", texto, re.IGNORECASE):
        return False
    if codigo == "CRITICO" and re.search(r"no hay peligro|sin peligro", texto, re.IGNORECASE):
        return False
    condicion = clasificacion.get("condicion")
    if condicion in ("dentro_del_texto_de_la_hoja", "dentro_de_los_limites_escritos"):
        if not re.search(r"queda entre el m[ií]nimo|entre el m[ií]nimo y el m[aá]ximo", texto, re.IGNORECASE):
            return False
        if re.search(r"no cumple|fuera de|supera|por encima|por debajo", texto, re.IGNORECASE):
            return False
    if condicion == "fuera_del_texto_de_la_hoja":
        if re.search(r"queda entre el m[ií]nimo|dentro de los l[ií]mites", texto, re.IGNORECASE):
            return False
    return True


def _paquete(mensaje: str, accion: str, nota: str) -> dict:
    return {"mensaje": mensaje, "accion": accion, "nota": nota, "origen": "deterministico", "modelo_usado": False}


def _primer_error(salida: dict) -> str:
    errores = salida.get("errores") or []
    if not errores:
        return ""
    primero = errores[0]
    if isinstance(primero, dict):
        return str(primero.get("mensaje") or primero.get("detalle") or "")
    return str(primero)


