"""Operaciones que el chat puede pedir. Ninguna la inventa el modelo."""

from __future__ import annotations

import logging
import time
import uuid

from services.consola_operacional import evaluar_pozo
from services.escenario_inicial import listar_pozos
from services.formato_numero import formato_visible
from services.resultados_en_vivo import ultimo

REGISTRO = ("calcular", "reglas", "simular", "comparar", "estado", "medidas", "presiones", "caudal", "frecuencia")
MAX_OPERACIONES = 4
MAX_LECTURA = 8
_BITACORA = logging.getLogger("huc.chat")


def ejecutar(decision: dict) -> dict:
    inicio = time.perf_counter()
    identificador = uuid.uuid4().hex[:12]
    intencion = decision.get("intencion")
    if intencion not in REGISTRO and intencion not in ("conceptual", "diferencia_pip", "seguimiento", "comparar_contexto", "rechazar_autorizacion", "aclarar", "consulta_esp", "fuera_de_alcance", "inventario"):
        _anotar(identificador, intencion, "", False, "", "rechazada", inicio, "operacion_desconocida")
        return _error("No puedo hacer esa consulta con la información que tengo.")
    if intencion in ("conceptual", "rechazar_autorizacion", "aclarar", "consulta_esp", "fuera_de_alcance", "inventario"):
        _anotar(identificador, intencion, intencion, True, "", "sin_motor", inicio, "")
        return {"ok": True, "intencion": intencion, "filas": [], "error": ""}
    pozos = [pozo for pozo in decision.get("pozos") or [] if pozo]
    if intencion == "comparar_contexto":
        _anotar(identificador, intencion, intencion, True, ",".join(pozos), "contexto", inicio, "")
        return {"ok": True, "intencion": intencion, "filas": [], "error": ""}
    if intencion == "comparar" and len(pozos) < 2:
        return _error("Para comparar necesito los dos pozos.")
    if not pozos:
        return _error("Necesito saber de qué pozo se trata.")
    tope = MAX_OPERACIONES if intencion == "simular" else MAX_LECTURA
    if len(pozos) > tope:
        return _error("La consulta pide demasiados pozos a la vez.")
    desconocidos = [pozo for pozo in pozos if pozo not in {item["pozo_id"] for item in listar_pozos()}]
    if desconocidos:
        _anotar(identificador, intencion, intencion, False, ",".join(desconocidos), "rechazada", inicio, "pozo_desconocido")
        return _error("No tengo ese pozo en el expediente que estoy consultando.")
    cambios = decision.get("cambios") if intencion == "simular" else {}
    if intencion == "simular" and not isinstance(cambios, dict):
        return _error("No puedo aplicar ese cambio.")
    meta = {item["pozo_id"]: item for item in listar_pozos()}
    filas = []
    omitidos = []
    for indice, pozo in enumerate(pozos[:tope]):
        ficha = meta.get(pozo) or {}
        if not ficha.get("evaluable") and intencion in ("estado", "medidas", "presiones", "caudal", "frecuencia", "comparar", "reglas"):
            omitidos.append(pozo)
            continue
        if not cambios:
            publicado = ultimo(pozo)
            if isinstance(publicado, dict) and publicado.get("resultados"):
                filas.append(_fila(publicado))
                continue
        try:
            codigo, cuerpo = evaluar_pozo(pozo, cambios or {}, f"chat-{identificador}", f"{identificador}-{indice}", False)
        except Exception as exc:  # noqa: BLE001 — un dataset sin motor no debe tumbar el resumen global
            _BITACORA.warning("chat omitió %s: %s", pozo, exc)
            if len(pozos) == 1:
                _anotar(identificador, intencion, "evaluar_pozo", False, pozo, "error_motor", inicio, "excepcion_motor")
                return _error(
                    f"No pude calcular el pozo {pozo} en este momento. "
                    "El expediente está registrado, pero el motor no completó la evaluación."
                )
            omitidos.append(pozo)
            continue
        if codigo != 200 or not cuerpo.get("ok"):
            if len(pozos) > 1:
                omitidos.append(pozo)
                continue
            _anotar(identificador, intencion, "evaluar_pozo", False, pozo, "error_motor", inicio, "calculo_no_completado")
            return _error(_mensaje_seguro(cuerpo))
        filas.append(_fila(cuerpo))
    if not filas:
        if omitidos:
            if len(omitidos) == 1:
                return _error(
                    f"El pozo {omitidos[0]} está registrado, pero no hay un resultado consultable "
                    "de su motor en este momento."
                )
            return _error("Esos pozos están registrados, pero su expediente aún no tiene motor consultable.")
        return _error("No hay un resultado consultable para esa pregunta.")
    _anotar(identificador, intencion, "evaluar_pozo", True, ",".join(p["pozo"] for p in filas), filas[0]["estado"] if filas else "", inicio, "")
    return {"ok": True, "intencion": intencion, "filas": filas, "error": "", "omitidos": omitidos}


def _fila(cuerpo: dict) -> dict:
    resultados = cuerpo.get("resultados") or {}
    pip = resultados.get("pip_ft") or {}
    thd = resultados.get("thd_total_ft") or {}
    caudal = resultados.get("caudal_a_producir_bfpd") or {}
    estado = cuerpo.get("estado") or {}
    return {
        "pozo": cuerpo.get("pozo_id"),
        "modo": cuerpo.get("modo"),
        "pip_ft": pip.get("valor"),
        "pip_visible": pip.get("valor_visible") or formato_visible(pip.get("valor")),
        "thd_ft": thd.get("valor"),
        "thd_visible": thd.get("valor_visible") or formato_visible(thd.get("valor")),
        "caudal_calculado_bfpd": caudal.get("valor"),
        "caudal_visible": caudal.get("valor_visible") or formato_visible(caudal.get("valor")),
        "estado": estado.get("codigo"),
        "codigo": estado.get("codigo"),
        "rotulo": estado.get("rotulo"),
        "reglas": list(cuerpo.get("reglas_activas") or []),
        "autorizada": cuerpo.get("recomendacion_operacional_autorizada") is True,
        "simulacion": cuerpo.get("modo") == "simulacion",
        "fuera_de_lo_observado": any("fuera del dominio observado" in str(aviso) for aviso in (cuerpo.get("advertencias_motor") or [])),
        "dataset_id": cuerpo.get("dataset_id") or "",
        "escenario_id": _escenario_visible(cuerpo.get("escenario_id")),
        "emitido_en": cuerpo.get("emitido_en") or cuerpo.get("momento_utc") or "",
        "magnitudes": _magnitudes(resultados),
        "entradas": cuerpo.get("entradas") if isinstance(cuerpo.get("entradas"), dict) else {},
        "mensaje": (cuerpo.get("texto") or {}).get("mensaje") if isinstance(cuerpo.get("texto"), dict) else "",
    }


def _escenario_visible(identificador) -> str:
    if not isinstance(identificador, str) or identificador.startswith("chat-"):
        return ""
    return identificador


def _magnitudes(resultados: dict) -> list[dict]:
    magnitudes = []
    for clave, item in resultados.items():
        if not isinstance(item, dict) or item.get("valor") is None:
            continue
        magnitudes.append({
            "id": clave,
            "nombre": item.get("nombre") or clave,
            "visible": item.get("valor_visible") or formato_visible(item.get("valor")),
            "unidad": item.get("unidad") or "",
            "tipo": "resultado",
            "descripcion": "",
        })
    return magnitudes


def _mensaje_seguro(cuerpo: dict) -> str:
    texto = cuerpo.get("error") if isinstance(cuerpo, dict) else ""
    if not isinstance(texto, str) or not texto.strip():
        return "No pude completar el cálculo con los datos de ese pozo."
    if any(marca in texto for marca in ("Traceback", "File ", "Error", "/", "\\")):
        return "No pude completar el cálculo con los datos de ese pozo."
    return texto.strip()


def _error(mensaje: str) -> dict:
    return {"ok": False, "intencion": "error", "filas": [], "error": mensaje}


def _anotar(identificador, intencion, operacion, autorizada, pozo, estado, inicio, error) -> None:
    _BITACORA.info(
        "chat id=%s intencion=%s operacion=%s autorizada=%s pozo=%s estado=%s ms=%s error=%s",
        identificador,
        intencion,
        operacion,
        autorizada,
        pozo,
        estado,
        int((time.perf_counter() - inicio) * 1000),
        error,
    )
