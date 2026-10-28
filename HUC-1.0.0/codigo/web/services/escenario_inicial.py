"""Valores iniciales leídos de la ficha del pozo. No inventa mediciones."""

from __future__ import annotations

from services.dataset_registry import descubrir
from services.rule_control_registry import controles_de_pozo

LEYENDA_SIN_TELEMETRIA = (
    "Escenario inicial basado en datos disponibles — no corresponde a telemetría en tiempo real."
)


def localizar(pozo_id: str) -> list[tuple]:
    if not pozo_id or not str(pozo_id).strip() or str(pozo_id) != str(pozo_id).strip():
        return []
    encontrados = []
    for ficha in descubrir():
        for pozo in ficha.pozos():
            if pozo.get("pozo_rotulo") == pozo_id:
                encontrados.append((ficha, pozo))
    return encontrados


def listar_pozos() -> list[dict]:
    pozos = []
    for ficha in descubrir():
        for pozo in ficha.pozos():
            rotulo = pozo.get("pozo_rotulo")
            if not rotulo:
                continue
            pozos.append({
                "pozo_id": rotulo,
                "hoja": pozo.get("hoja"),
                "dataset_id": ficha.identificador,
                "bomba_referencia": pozo.get("bomba_referencia"),
                "evaluable": ficha.puede_evaluar,
                "identidad": pozo.get("estado_identidad") or "No disponible",
            })
    return pozos


def escenario_de(pozo: dict, ficha) -> dict:
    frecuencias = []
    for otro in ficha.pozos():
        condiciones_otras = otro.get("condiciones_registradas") if isinstance(otro.get("condiciones_registradas"), dict) else {}
        frecuencias.append(_numero(condiciones_otras.get("frecuencia_hz")))
    controles = controles_de_pozo(pozo, ficha, frecuencias)
    lecturas = [
        _lectura("thd_total_ft", "THD", "ft", None, "calculado",
                 "Salida del balance. No entra en RC-BES-01, 02 ni 03."),
        _lectura("pip_ft", "PIP", "ft", None, "calculado",
                 "Salida de la celda. No entra en las reglas de caudal."),
    ]
    return {
        "pozo_id": pozo.get("pozo_rotulo"),
        "hoja": pozo.get("hoja"),
        "dataset_id": ficha.identificador,
        "bomba_referencia": pozo.get("bomba_referencia"),
        "identidad": pozo.get("estado_identidad") or "No disponible",
        "evaluable": bool(ficha.puede_evaluar and any(control.get("valor_inicial") is not None for control in controles)),
        "procedencia": "escenario_inicial",
        "leyenda": "",
        "fecha_medicion": pozo.get("fecha_medicion"),
        "fecha_en_la_hoja": pozo.get("fecha_en_la_hoja"),
        "fecha_es_today": pozo.get("fecha_es_today"),
        "calidad": pozo.get("calidad"),
        "controles": controles,
        "lecturas": lecturas,
        "limitaciones": list(pozo.get("limitaciones") or []),
    }


def _lectura(identificador, nombre, unidad, valor, origen, nota) -> dict:
    return {
        "id": identificador,
        "nombre": nombre,
        "unidad": unidad,
        "valor": valor,
        "origen": origen,
        "nota": nota,
    }


def _numero(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return None
    return float(valor)
