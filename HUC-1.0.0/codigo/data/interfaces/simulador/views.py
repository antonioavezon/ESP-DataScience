import hmac
import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from data.servicios.publicador import acuse as leer_acuse
from data.servicios.publicador import publicar
from data.simuladores.automatico import Secuencia
from data.simuladores.escenarios import base as ficha_base
from data.simuladores.escenarios import mensaje, pozos as listar, validar

_SECUENCIA = Secuencia()


def _autenticado(request) -> bool:
    return request.session.get("huc_operador") == settings.HUC_SIM_USUARIO


def _exigir(request):
    if _autenticado(request):
        return None
    return JsonResponse({"error": "Se requiere autenticación para modificar el escenario."}, status=401)


def inicio(request):
    return render(request, "simulador/index.html", {"pozos": listar(), "autenticado": _autenticado(request)})


@require_GET
def sesion(request):
    return JsonResponse({"autenticado": _autenticado(request)})


@require_POST
def acceder(request):
    try:
        cuerpo = json.loads(request.body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"error": "El cuerpo no es JSON válido."}, status=400)
    usuario = str(cuerpo.get("usuario") or "")
    clave = str(cuerpo.get("clave") or "")
    esperada = settings.HUC_SIM_CLAVE
    if not esperada:
        return JsonResponse({"error": "El simulador no tiene clave configurada."}, status=503)
    if not hmac.compare_digest(usuario, settings.HUC_SIM_USUARIO) or not hmac.compare_digest(clave, esperada):
        return JsonResponse({"error": "Usuario o clave incorrectos."}, status=401)
    request.session["huc_operador"] = settings.HUC_SIM_USUARIO
    return JsonResponse({"autenticado": True})


@require_GET
def pozos(request):
    return JsonResponse({"pozos": listar()})


@require_GET
def base(request, pozo_id: str):
    ficha = ficha_base(pozo_id)
    if ficha is None:
        return JsonResponse({"error": "Ese pozo no está en el inventario."}, status=404)
    return JsonResponse(ficha)


@require_POST
def aplicar(request, pozo_id: str):
    rechazo = _exigir(request)
    if rechazo:
        return rechazo
    try:
        cuerpo = json.loads(request.body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"error": "El cuerpo no es JSON válido."}, status=400)
    deseados = cuerpo.get("valores") if isinstance(cuerpo, dict) else None
    cambios, error = validar(pozo_id, deseados or {})
    if error:
        return JsonResponse({"publicado": False, "error": error}, status=400)
    documento = mensaje(pozo_id, cambios or {})
    fallo = publicar(documento)
    if fallo:
        return JsonResponse({"publicado": False, "error": fallo}, status=503)
    return JsonResponse({
        "publicado": True,
        "evaluacion_id": documento["evaluacion_id"],
        "escenario_id": documento["escenario_id"],
        "pozo_id": pozo_id,
    })


@require_POST
def restaurar(request, pozo_id: str):
    rechazo = _exigir(request)
    if rechazo:
        return rechazo
    ficha = ficha_base(pozo_id)
    if ficha is None or not ficha["evaluable"]:
        return JsonResponse({"publicado": False, "error": "Ese pozo no admite restauración."}, status=400)
    documento = mensaje(pozo_id, {})
    fallo = publicar(documento)
    if fallo:
        return JsonResponse({"publicado": False, "error": fallo}, status=503)
    return JsonResponse({
        "publicado": True,
        "evaluacion_id": documento["evaluacion_id"],
        "escenario_id": documento["escenario_id"],
    })


@require_GET
def acuse(request, pozo_id: str, evaluacion_id: str):
    documento = leer_acuse(evaluacion_id)
    if documento is None:
        return JsonResponse({"recibido": False, "pozo_id": pozo_id, "evaluacion_id": evaluacion_id})
    if documento.get("pozo_id") != pozo_id:
        return JsonResponse({"recibido": False, "error": "El acuse corresponde a otro pozo."}, status=409)
    return JsonResponse({"recibido": True, **documento})


@require_POST
def automatica(request, pozo_id: str):
    rechazo = _exigir(request)
    if rechazo:
        return rechazo
    try:
        cuerpo = json.loads(request.body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"error": "El cuerpo no es JSON válido."}, status=400)
    accion = cuerpo.get("accion")
    if accion == "pausar":
        _SECUENCIA.pausar(pozo_id)
    elif accion == "reanudar":
        _SECUENCIA.reanudar(pozo_id)
    elif accion == "detener":
        _SECUENCIA.detener(pozo_id)
    elif accion == "iniciar":
        try:
            intervalo = float(cuerpo.get("intervalo_s"))
            duracion = float(cuerpo.get("duracion_s"))
            semilla = int(cuerpo.get("semilla"))
        except (TypeError, ValueError):
            return JsonResponse({"error": "Intervalo, duración y semilla son obligatorios."}, status=400)

        def enviar(pozo, valores, semilla_paso):
            cambios, error = validar(pozo, valores)
            if error or not cambios:
                return
            documento = mensaje(pozo, cambios, semilla=semilla_paso)
            publicar(documento)

        error = _SECUENCIA.iniciar(pozo_id, intervalo, duracion, semilla, enviar)
        if error:
            return JsonResponse({"error": error}, status=400)
    else:
        return JsonResponse({"error": "Acción no admitida."}, status=400)
    return JsonResponse({"pozo_id": pozo_id, "fase": _SECUENCIA.estado(pozo_id)})
