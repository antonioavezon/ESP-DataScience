from django.shortcuts import redirect, render

from apps.core.context import preferencias
from services.dataset_registry import obtener
from services.huc_adapter import UNIDADES


def indice(request):
    prefs = preferencias(request)
    seleccion = obtener(prefs["dataset_id"]) if prefs["dataset_id"] else None
    resultado = request.session.get("ultima_evaluacion")
    return render(request, "evaluaciones/indice.html", {
        "seleccion": seleccion,
        "pozos": seleccion.pozos() if seleccion else [],
        "entradas": UNIDADES,
        "resultado": resultado,
        "adaptador_listo": bool(seleccion and seleccion.puede_evaluar),
    })


def ejecutar(request):
    return redirect("evaluaciones")
