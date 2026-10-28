import time

from services.dataset_registry import descubrir
from services.ollama_client import ClienteOllama, configuracion

_CACHE = {"momento": 0.0, "estado": None}


def estado_ollama(forzar: bool = False) -> dict:
    ahora = time.monotonic()
    if not forzar and _CACHE["estado"] is not None and ahora - _CACHE["momento"] < 15:
        return _CACHE["estado"]
    cfg = configuracion()
    cliente = ClienteOllama(cfg["base_url"], min(8, cfg["timeout_s"]))
    try:
        inventario = cliente.modelos()
    finally:
        cliente.cerrar()
    estado = {
        "disponible": inventario.ok,
        "error": inventario.error,
        "modelos": inventario.modelos,
        "base_url": cfg["base_url"],
    }
    _CACHE["momento"] = ahora
    _CACHE["estado"] = estado
    return estado


def preferencias(request) -> dict:
    cfg = configuracion()
    dataset = request.session.get("dataset_id")
    if not dataset:
        en_uso = [ficha for ficha in descubrir() if ficha.ciclo == "en_uso"]
        dataset = en_uso[0].identificador if en_uso else ""
    return {
        "modelo": request.session.get("modelo") or cfg["modelo"],
        "timeout_s": int(request.session.get("timeout_s") or cfg["timeout_s"]),
        "num_predict": int(request.session.get("num_predict") or cfg["num_predict"]),
        "dataset_id": dataset,
        "base_url": cfg["base_url"],
    }


def navegacion(request):
    from services.escenario_inicial import listar_pozos
    from services.resultados_en_vivo import filas

    return {"estados_pozos": filas(listar_pozos())}
