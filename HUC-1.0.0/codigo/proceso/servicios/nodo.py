"""Recibe escenarios, ejecuta el motor y publica el resultado vigente."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone

from proceso.contratos.mensajes import (
    TOPIC_SERVICIO,
    validar_escenario,
    topic_estado,
    topic_resultado,
)
from proceso.motores.ejecutor import evaluar, publicar_linea_base

_VISTOS: set[str] = set()
_RECIENTES: dict[str, str] = {}
_CANDADO = threading.Lock()


def ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def procesar(documento: dict) -> dict:
    error = validar_escenario(documento)
    pozo = documento.get("pozo_id") if isinstance(documento, dict) else ""
    evaluacion = documento.get("evaluacion_id") if isinstance(documento, dict) else ""
    if error:
        return _error(pozo if isinstance(pozo, str) else "", evaluacion if isinstance(evaluacion, str) else "", "error_validacion", error)
    with _CANDADO:
        if evaluacion in _VISTOS:
            return {"omitido": True, "motivo": "duplicado", "evaluacion_id": evaluacion}
        previo = _RECIENTES.get(pozo)
        if previo and documento["emitido_en"] < previo:
            return {"omitido": True, "motivo": "obsoleto", "evaluacion_id": evaluacion}
        _VISTOS.add(evaluacion)
        _RECIENTES[pozo] = documento["emitido_en"]
    try:
        _codigo, cuerpo = evaluar(
            pozo,
            documento.get("controles") or {},
            documento.get("escenario_id") or "",
            evaluacion,
            False,
        )
    except Exception as exc:
        return _error(pozo, evaluacion, "error_ejecucion", exc.__class__.__name__)
    return _desde_motor(documento, cuerpo)


def _desde_motor(documento: dict, cuerpo: dict) -> dict:
    estado = cuerpo.get("estado") if isinstance(cuerpo, dict) else {}
    codigo = estado.get("codigo") if isinstance(estado, dict) else ""
    motor = cuerpo.get("estado_motor")
    if codigo == "ERROR_CALCULO" or motor in ("entrada_invalida", "error_interno"):
        publicacion = "error_validacion" if motor == "entrada_invalida" else "error_ejecucion"
    elif motor == "no_disponible":
        publicacion = "calculo_no_disponible"
    elif (codigo == "SIN_DATOS" or motor == "no_evaluable") and not cuerpo.get("resultados"):
        publicacion = "datos_insuficientes"
    elif cuerpo.get("ok"):
        publicacion = "calculo_exitoso"
    else:
        publicacion = "error_ejecucion"
    return {
        "version": "1",
        "origen": "proceso",
        "omitido": False,
        "dataset_id": documento.get("dataset_id"),
        "pozo_id": documento.get("pozo_id"),
        "escenario_id": cuerpo.get("escenario_id") or documento.get("escenario_id"),
        "evaluacion_id": documento.get("evaluacion_id"),
        "emitido_en": ahora(),
        "emitido_en_escenario": documento.get("emitido_en"),
        "modo": cuerpo.get("modo") or documento.get("modo"),
        "origen_valores": "simulado" if (cuerpo.get("modo") == "simulacion" or documento.get("modo") == "simulacion") else "hoja",
        "version_contrato": "1.3.0",
        "estado_publicacion": publicacion,
        "estado": estado,
        "texto": cuerpo.get("texto") or {},
        "resultados": cuerpo.get("resultados") or {},
        "modificadas": cuerpo.get("modificadas") or [],
        "reglas_activas": cuerpo.get("reglas_activas") or [],
        "recomendacion_operacional_autorizada": cuerpo.get("recomendacion_operacional_autorizada"),
        "entradas": documento.get("controles") or {},
        "proceso_disponible": True,
    }


def _error(pozo: str, evaluacion: str, publicacion: str, detalle: str) -> dict:
    return {
        "version": "1",
        "origen": "proceso",
        "omitido": False,
        "pozo_id": pozo,
        "evaluacion_id": evaluacion,
        "emitido_en": ahora(),
        "modo": "simulacion",
        "origen_valores": "simulado",
        "version_contrato": "1.3.0",
        "estado_publicacion": publicacion,
        "estado": {
            "codigo": "ERROR_CALCULO",
            "rotulo": "CÁLCULO NO COMPLETADO",
            "tono": "sin-clasificacion",
            "clasificacion_valida": False,
        },
        "texto": {"mensaje": detalle, "accion": "", "origen": "deterministico"},
        "resultados": {},
        "proceso_disponible": True,
    }


def atender(cliente, documento: dict) -> None:
    resultado = procesar(documento)
    if resultado.get("omitido"):
        return
    pozo = resultado.get("pozo_id") or ""
    if not pozo:
        return
    carga = json.dumps(resultado, ensure_ascii=False)
    cliente.publish(topic_resultado(pozo), carga, qos=1, retain=True)
    cliente.publish(topic_estado(pozo), json.dumps({
        "version": "1",
        "pozo_id": pozo,
        "evaluacion_id": resultado.get("evaluacion_id"),
        "emitido_en": resultado.get("emitido_en"),
        "codigo": (resultado.get("estado") or {}).get("codigo"),
        "rotulo": (resultado.get("estado") or {}).get("rotulo"),
        "tono": (resultado.get("estado") or {}).get("tono"),
        "clasificacion_valida": (resultado.get("estado") or {}).get("clasificacion_valida"),
        "modo": resultado.get("modo"),
        "origen_valores": resultado.get("origen_valores"),
    }, ensure_ascii=False), qos=1, retain=True)


def linea_base(cliente) -> None:
    for item in publicar_linea_base():
        cuerpo = item["cuerpo"]
        pozo = cuerpo.get("pozo_id")
        if not pozo:
            continue
        documento = {
            "version": "1",
            "origen": "data",
            "dataset_id": cuerpo.get("dataset_id") or "",
            "pozo_id": pozo,
            "escenario_id": f"base-{pozo}",
            "evaluacion_id": f"base-{pozo}",
            "emitido_en": ahora(),
            "modo": "escenario_inicial",
            "version_contrato": "1.3.0",
            "controles": {},
            "valores_originales": {},
            "origen_valores": "simulado",
        }
        with _CANDADO:
            _VISTOS.add(documento["evaluacion_id"])
            _RECIENTES[pozo] = documento["emitido_en"]
        resultado = _desde_motor(documento, cuerpo)
        resultado["origen_valores"] = "hoja"
        resultado["modo"] = "escenario_inicial"
        cliente.publish(topic_resultado(pozo), json.dumps(resultado, ensure_ascii=False), qos=1, retain=True)
        cliente.publish(topic_estado(pozo), json.dumps({
            "version": "1",
            "pozo_id": pozo,
            "evaluacion_id": resultado["evaluacion_id"],
            "emitido_en": resultado["emitido_en"],
            "codigo": resultado["estado"].get("codigo"),
            "rotulo": resultado["estado"].get("rotulo"),
            "tono": resultado["estado"].get("tono"),
            "clasificacion_valida": resultado["estado"].get("clasificacion_valida"),
            "modo": "escenario_inicial",
            "origen_valores": "hoja",
        }, ensure_ascii=False), qos=1, retain=True)


def latido(cliente) -> None:
    marca = ahora()
    try:
        from pathlib import Path
        Path("/tmp/huc-proceso-vivo").write_text(marca, encoding="utf-8")
    except OSError:
        pass
    cliente.publish(TOPIC_SERVICIO, json.dumps({
        "version": "1",
        "disponible": True,
        "emitido_en": marca,
    }), qos=0, retain=True)
