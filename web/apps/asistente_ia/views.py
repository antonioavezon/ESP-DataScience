from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST

from apps.core.context import estado_ollama, preferencias
from services.chat_orquestador import responder
from services.chat_contrato import render_html as render_contrato, validar as validar_contrato
from services.chat_presentacion import (
    datasets_disponibles,
    etiqueta_alcance,
    pozos_disponibles,
    render_html as render_legacy,
)
from services.dataset_registry import obtener
from services.ollama_client import PREDICT_MAXIMO, TIMEOUT_MAXIMO, ClienteOllama, configuracion

CONSULTA_TECNICA = "Según el contexto, define PIP en una frase. No inventes fórmulas ni mediciones."
HISTORIAL_MAXIMO = 20


def _cliente(timeout: float) -> ClienteOllama:
    cfg = configuracion()
    return ClienteOllama(cfg["base_url"], timeout)


def _dataset_sesion(request) -> str:
    """ALL = todos los datasets. No sustituye silenciosamente por BES-jun."""
    crudo = request.session.get("asistente_dataset_id")
    if crudo is None:
        return "ALL"
    texto = str(crudo).strip()
    if texto in ("", "ALL", "all", "Todos"):
        return "ALL"
    if obtener(texto) is None:
        return "ALL"
    return texto


def _parsear_pozo(crudo: str) -> tuple[str | None, str | None]:
    """Acepta 'QF-084' o 'BES-jun::QF-084' cuando Dataset=Todos."""
    texto = (crudo or "").strip()
    if not texto:
        return None, None
    if "::" in texto:
        dataset, pozo = texto.split("::", 1)
        return (dataset.strip() or None), (pozo.strip() or None)
    return None, texto


def _pozo_sesion(request, dataset_id: str) -> tuple[str | None, str | None]:
    """Devuelve (dataset_del_pozo, pozo_id). El dataset del pozo aplica si Dataset=Todos."""
    crudo = (request.session.get("asistente_pozo_id") or "").strip()
    if not crudo:
        return None, None
    ds_pozo, pozo_id = _parsear_pozo(crudo)
    disponibles = pozos_disponibles(None if dataset_id == "ALL" else dataset_id)
    if dataset_id == "ALL" and ds_pozo and pozo_id:
        for item in disponibles:
            if item["dataset_id"] == ds_pozo and item["pozo_id"] == pozo_id:
                return ds_pozo, pozo_id
        return None, None
    if pozo_id and any(item["pozo_id"] == pozo_id for item in disponibles):
        if dataset_id != "ALL":
            return dataset_id, pozo_id
        coincidencias = [item for item in disponibles if item["pozo_id"] == pozo_id]
        if len(coincidencias) == 1:
            return coincidencias[0]["dataset_id"], pozo_id
        if ds_pozo:
            for item in coincidencias:
                if item["dataset_id"] == ds_pozo:
                    return ds_pozo, pozo_id
        return None, None
    return None, None


def _alcance(dataset_id: str, pozo_id: str | None, dataset_pozo: str | None = None) -> dict:
    if dataset_id == "ALL":
        if pozo_id and dataset_pozo:
            return {"dataset": "Todos", "pozo": f"{dataset_pozo} · {pozo_id}"}
        return {"dataset": "Todos", "pozo": "Todos"}
    return {
        "dataset": dataset_id,
        "pozo": pozo_id or "Todos",
    }


def _fuente_visible(inferencia: dict) -> str:
    alcance = inferencia.get("alcance") if isinstance(inferencia.get("alcance"), dict) else {}
    if alcance:
        return f"Fuente: {etiqueta_alcance(alcance)}"
    dataset = inferencia.get("dataset") or ""
    pozo = inferencia.get("pozo") or ""
    if dataset and pozo and pozo != "Todos":
        return f"Fuente: {dataset} · Pozo: {pozo}"
    if dataset:
        return f"Fuente: {dataset} · Pozos: Todos"
    return "Fuente: cálculo del expediente"


def _guardar_dataset(request, crudo: str) -> str:
    texto = (crudo or "").strip()
    if texto in ("", "ALL", "all", "Todos"):
        request.session["asistente_dataset_id"] = "ALL"
    elif obtener(texto) is not None:
        request.session["asistente_dataset_id"] = texto
    else:
        request.session["asistente_dataset_id"] = "ALL"
    return _dataset_sesion(request)


def _pagina(request, prefs, error: str | None = None):
    dataset_id = _dataset_sesion(request)
    dataset_pozo, pozo_id = _pozo_sesion(request, dataset_id)
    alcance = _alcance(dataset_id, pozo_id, dataset_pozo)
    historial = request.session.get("historial_asistente") or []
    pozo_valor = ""
    if pozo_id and dataset_id == "ALL" and dataset_pozo:
        pozo_valor = f"{dataset_pozo}::{pozo_id}"
    elif pozo_id:
        pozo_valor = pozo_id
    return {
        "prefs": prefs,
        "datasets": datasets_disponibles(),
        "dataset_seleccionado": dataset_id,
        "pozos": pozos_disponibles(None if dataset_id == "ALL" else dataset_id),
        "pozo_seleccionado": pozo_valor,
        "etiqueta_contexto": etiqueta_alcance(alcance),
        "historial": historial,
        "error": error,
        "respuesta": request.session.get("ultima_inferencia"),
    }


def consultar(request):
    prefs = preferencias(request)
    if "dataset_id" in request.GET:
        anterior = _dataset_sesion(request)
        nuevo = _guardar_dataset(request, request.GET.get("dataset_id") or "")
        if nuevo != anterior:
            request.session["asistente_pozo_id"] = ""
        return redirect("asistente")
    return render(request, "asistente_ia/consultar.html", _pagina(request, prefs))


@require_POST
def enviar(request):
    prefs = preferencias(request)
    if "dataset_id" in request.POST:
        _guardar_dataset(request, request.POST.get("dataset_id") or "")
    dataset_id = _dataset_sesion(request)

    if "pozo_id" in request.POST:
        request.session["asistente_pozo_id"] = (request.POST.get("pozo_id") or "").strip()
    dataset_pozo, pozo_id = _pozo_sesion(request, dataset_id)
    # Pozo concreto bajo "Todos": el motor se acota a su dataset; el encabezado sigue en Todos.
    dataset_consulta = dataset_pozo if (dataset_id == "ALL" and pozo_id and dataset_pozo) else dataset_id
    alcance = _alcance(dataset_id, pozo_id, dataset_pozo)
    ambito = "pozo" if pozo_id else "dataset"
    consulta = (request.POST.get("consulta") or "").strip()
    if not consulta:
        return render(
            request,
            "asistente_ia/consultar.html",
            _pagina(request, prefs, "Escribe una consulta antes de enviar."),
            status=400,
        )

    cliente = _cliente(prefs["timeout_s"])
    try:
        resultado = responder(
            consulta,
            pozo_id,
            request.session.get("contexto_chat"),
            cliente,
            modelo=prefs["modelo"],
            num_predict=prefs["num_predict"],
            dataset_id=dataset_consulta,
            ambito=ambito,
            alcance=alcance,
        )
    finally:
        cliente.cerrar()

    inferencia = resultado.get("inferencia") or {}
    # Alcance efectivo: el orquestador puede haber fijado pozo/dataset citados en el texto.
    alcance_efectivo = inferencia.get("alcance") if isinstance(inferencia.get("alcance"), dict) else alcance
    if not isinstance(inferencia.get("contenido"), str) or not inferencia.get("contenido", "").strip():
        inferencia = {
            **inferencia,
            "ok": False,
            "contenido": "No pude armar una respuesta con la información disponible.",
            "error": "respuesta_vacia",
            "consulta": consulta[:500],
            "alcance": alcance_efectivo,
            "estructura": None,
        }
    inferencia["alcance"] = alcance_efectivo
    inferencia["fuente_visible"] = _fuente_visible(inferencia)
    inferencia["etiqueta"] = etiqueta_alcance(alcance_efectivo)
    estructura = inferencia.get("estructura") or {}
    if isinstance(estructura, dict) and estructura.get("schema_version") == "1.0":
        inferencia["html"] = mark_safe(render_contrato(estructura))
        inferencia["contrato_ok"] = validar_contrato(estructura)[0]
    elif estructura:
        inferencia["html"] = mark_safe(render_legacy(estructura))
        inferencia["contrato_ok"] = False
    else:
        inferencia["html"] = ""
        inferencia["contrato_ok"] = False

    request.session["contexto_chat"] = resultado.get("contexto") or {}
    request.session["ultima_inferencia"] = {
        k: v for k, v in inferencia.items() if k != "html"
    }
    historial = list(request.session.get("historial_asistente") or [])
    historial.append({
        "consulta": consulta,
        "contenido": inferencia.get("contenido") or "",
        "ok": bool(inferencia.get("ok")),
        "etiqueta": etiqueta_alcance(alcance_efectivo),
        "fuente": inferencia.get("fuente_visible") or "",
        "estructura": inferencia.get("estructura"),
    })
    request.session["historial_asistente"] = historial[-HISTORIAL_MAXIMO:]
    return redirect("asistente")


@require_POST
def borrar(request):
    request.session.pop("ultima_inferencia", None)
    request.session.pop("contexto_chat", None)
    request.session.pop("historial_asistente", None)
    return redirect("asistente")


def configuracion_ia(request):
    prefs = preferencias(request)
    ollama = estado_ollama(forzar=True)
    aviso = ""
    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "guardar":
            modelo = (request.POST.get("modelo") or "").strip()
            nombres = {item["nombre"] for item in ollama["modelos"]}
            if ollama["disponible"] and modelo not in nombres:
                aviso = f"El modelo {modelo} no está instalado. Se mantiene la selección anterior."
            elif modelo:
                request.session["modelo"] = modelo
            try:
                timeout = int(request.POST.get("timeout_s") or prefs["timeout_s"])
                predict = int(request.POST.get("num_predict") or prefs["num_predict"])
            except ValueError:
                aviso = (aviso + " Los límites deben ser números enteros.").strip()
            else:
                request.session["timeout_s"] = min(TIMEOUT_MAXIMO, max(5, timeout))
                request.session["num_predict"] = min(PREDICT_MAXIMO, max(32, predict))
            if not aviso:
                return redirect("configuracion_ia")
        elif accion == "conexion":
            request.session["prueba_conexion"] = {
                "ok": ollama["disponible"],
                "error": ollama["error"],
                "cantidad": len(ollama["modelos"]),
            }
            return redirect("configuracion_ia")
        elif accion == "tecnica":
            from services.technical_context import mensajes as armar

            construidos, contexto = armar(CONSULTA_TECNICA, obtener(prefs["dataset_id"]) if prefs["dataset_id"] else None)
            cliente = _cliente(prefs["timeout_s"])
            try:
                inferencia = cliente.consultar(prefs["modelo"], construidos, min(prefs["num_predict"], 256))
            finally:
                cliente.cerrar()
            request.session["ultima_inferencia"] = {
                **inferencia.a_dict(),
                "consulta": CONSULTA_TECNICA,
                "fuentes": contexto["fuentes"],
                "fuente_visible": "Fuente: prueba técnica de configuración",
                "pozo": None,
                "dataset": prefs["dataset_id"],
                "prueba": "tecnica",
            }
            return redirect("configuracion_ia")
        prefs = preferencias(request)
    nombres = {item["nombre"] for item in ollama["modelos"]}
    return render(request, "asistente_ia/configuracion.html", {
        "prefs": prefs,
        "ollama": ollama,
        "modelo_listado": prefs["modelo"] in nombres,
        "aviso": aviso,
        "prueba_conexion": request.session.get("prueba_conexion"),
        "respuesta": request.session.get("ultima_inferencia"),
        "consulta_tecnica": CONSULTA_TECNICA,
        "predict_maximo": PREDICT_MAXIMO,
        "timeout_maximo": TIMEOUT_MAXIMO,
    })
