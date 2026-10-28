from django.shortcuts import render

from services.dataset_registry import descubrir
from services.escenario_inicial import listar_pozos
from services.resultados_en_vivo import filas


def inicio(request):
    pozos = listar_pozos()
    por_pozo = {fila["pozo_id"]: fila for fila in filas(pozos)}
    pedido = request.GET.get("pozo")
    elegido = por_pozo.get(pedido) if pedido in por_pozo else (next(iter(por_pozo.values()), None))
    return render(request, "core/consola.html", {"pozos": pozos, "estado_pantalla": elegido})


def administracion(request):
    fichas = descubrir()
    pozos = []
    evaluaciones = []
    for ficha in fichas:
        pozos.extend(ficha.pozos())
        evaluaciones.extend(ficha.resultados_csv())
    return render(request, "core/administracion.html", {
        "fichas": fichas,
        "cantidad_datasets": len(fichas),
        "cantidad_pozos": len(pozos),
        "hay_pozos_verificables": any(ficha.archivos.get("pozos") for ficha in fichas),
        "cantidad_resultados": len(evaluaciones),
        "hay_resultados": any(ficha.archivos.get("resultados") for ficha in fichas),
        "motores": [ficha for ficha in fichas if ficha.puede_evaluar],
        "sin_motor": [ficha for ficha in fichas if not ficha.puede_evaluar],
        "advertencias": [
            (ficha.identificador, texto)
            for ficha in fichas
            for texto in ficha.limitaciones
        ],
    })


def acerca(request):
    return render(request, "core/acerca.html")
