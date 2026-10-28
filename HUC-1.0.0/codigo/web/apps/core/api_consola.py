import os

import httpx
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from services.escenario_inicial import escenario_de, listar_pozos, localizar
from services.resultados_en_vivo import filas, proceso_vigente, ultimo


@require_GET
def estados(request):
    pozos = listar_pozos()
    return JsonResponse({
        "fuente": "proceso",
        "proceso_disponible": proceso_vigente(),
        "pozos": filas(pozos),
    })


@require_GET
def pozos(request):
    return JsonResponse({"pozos": listar_pozos()})


@require_GET
def escenario(request, pozo_id: str):
    encontrados = localizar(pozo_id)
    if not encontrados:
        return JsonResponse({"error": "Ese pozo no está en una ficha de integración."}, status=404)
    if len(encontrados) > 1:
        return JsonResponse({"error": "Hay más de un pozo con ese identificador."}, status=409)
    ficha, pozo = encontrados[0]
    return JsonResponse(escenario_de(pozo, ficha))


@require_GET
def resultado(request, pozo_id: str):
    if not localizar(pozo_id):
        return JsonResponse({"error": "Ese pozo no está en una ficha de integración."}, status=404)
    documento = ultimo(pozo_id)
    if documento is None:
        return JsonResponse({
            "pozo_id": pozo_id,
            "disponible": False,
            "proceso_disponible": proceso_vigente(),
            "estado": {
                "codigo": "SIN_DATOS",
                "rotulo": "SIN RESULTADO",
                "tono": "sin-clasificacion",
                "clasificacion_valida": False,
            },
            "texto": {"mensaje": "No hay un resultado publicado.", "accion": ""},
            "resultados": {},
            "referencia": _referencia(pozo_id),
        })
    return JsonResponse({
        **documento,
        "disponible": True,
        "proceso_disponible": proceso_vigente(),
        "referencia": _referencia(pozo_id),
    })


def _referencia(pozo_id: str) -> dict:
    encontrados = localizar(pozo_id)
    if len(encontrados) != 1:
        return {}
    ficha, pozo = encontrados[0]
    escenario = escenario_de(pozo, ficha)
    salida = {}
    for control in escenario.get("controles") or []:
        identificador = control.get("id")
        if not identificador:
            continue
        paso = (control.get("recorrido") or {}).get("paso")
        salida[identificador] = {
            "nombre": control.get("nombre") or identificador,
            "unidad": control.get("unidad") or "",
            "valor": control.get("valor_inicial"),
            "decimales": _decimales(paso),
        }
    return salida


def _decimales(paso) -> int | None:
    if isinstance(paso, bool) or not isinstance(paso, (int, float)) or paso <= 0 or paso >= 1:
        return None
    texto = f"{float(paso):.6f}".rstrip("0")
    return len(texto.split(".")[1]) if "." in texto else None


def explicacion(request, pozo_id: str):
    documento = ultimo(pozo_id)
    if documento is None:
        return JsonResponse({
            "estado_generacion": "respaldo",
            "explicacion": "No hay un resultado publicado.",
            "modelo": "",
            "advertencias": ["La explicación lingüística no está disponible."],
        })
    try:
        destino = os.environ.get("HUC_IA_URL", "http://127.0.0.1:8002").rstrip("/")
        respuesta = httpx.post(destino + "/v1/explicar", json=documento, timeout=50.0)
        respuesta.raise_for_status()
        return JsonResponse(respuesta.json())
    except (httpx.HTTPError, ValueError):
        texto = documento.get("texto") if isinstance(documento.get("texto"), dict) else {}
        return JsonResponse({
            "estado_generacion": "respaldo",
            "explicacion": texto.get("mensaje") or "",
            "evaluacion_id": documento.get("evaluacion_id"),
            "modelo": "",
            "advertencias": ["La explicación lingüística no está disponible."],
        })
