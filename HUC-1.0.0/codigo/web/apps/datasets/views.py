from django.http import Http404
from django.shortcuts import redirect, render

from services.dataset_registry import descubrir, obtener
from services.huc_adapter import adaptador_para


def lista(request):
    return render(request, "datasets/lista.html", {"fichas": descubrir()})


def detalle(request, identificador: str):
    ficha = obtener(identificador)
    if ficha is None:
        raise Http404("Dataset no registrado")
    adaptador = adaptador_para(ficha)
    return render(request, "datasets/detalle.html", {
        "ficha": ficha,
        "pozos": ficha.pozos(),
        "variables": ficha.variables(),
        "reglas": ficha.reglas(),
        "resultados": ficha.resultados_csv(),
        "notas": adaptador.notas_resultado(),
        "manifiesto": ficha.manifiesto or {},
    })


def seleccionar(request, identificador: str):
    if request.method != "POST":
        raise Http404()
    ficha = obtener(identificador)
    if ficha is None:
        raise Http404("Dataset no registrado")
    request.session["dataset_id"] = ficha.identificador
    return redirect("detalle_dataset", identificador=ficha.identificador)


def pozo(request, identificador: str, pozo_id: str):
    ficha = obtener(identificador)
    if ficha is None:
        raise Http404("Dataset no registrado")
    registro = next((item for item in ficha.pozos() if item.get("pozo_rotulo") == pozo_id), None)
    if registro is None:
        raise Http404("Pozo no registrado")
    fila = next((item for item in ficha.resultados_csv() if item.get("pozo") == pozo_id), None)
    return render(request, "datasets/pozo.html", {
        "ficha": ficha,
        "pozo": registro,
        "resultado": fila,
        "notas": adaptador_para(ficha).notas_resultado(),
        "variables": ficha.variables(),
        "reglas": ficha.reglas(),
    })
