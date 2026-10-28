"""Controles de la consola a partir de las reglas ejecutables.

Solo entran variables que una regla con disposición preliminar u operacional
usa y que el contrato acepta como variable operacional. Los límites escritos
y la frecuencia base de la curva no son mandos: son el umbral y la base del
escalamiento. RC-BES-04 no se evalúa y no genera un control.
"""

from __future__ import annotations

import sys

from services.dataset_registry import FichaDataset

VARIABLES_OPERACIONALES = frozenset({
    "caudal_operacion_bfpd",
    "frecuencia_hz",
    "presion_sensor_psi",
    "thp_psi",
    "api_deg",
    "bsw_numero",
    "temperatura_c",
})

NOMBRES = {
    "frecuencia_hz": "Frecuencia de operación",
    "caudal_operacion_bfpd": "Caudal de operación",
}


def _modulos(ficha: FichaDataset):
    if ficha.identificador != "BES-jun" or not ficha.puede_evaluar:
        return None
    src = ficha.ruta / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    from reglas.candidatas_bes_jun import FRECUENCIA_BASE_LIMITES_HZ, limites_a_frecuencia
    from reglas.catalogo import REGLAS, disposicion

    return REGLAS, disposicion, limites_a_frecuencia, FRECUENCIA_BASE_LIMITES_HZ


def reglas_ejecutables(ficha: FichaDataset) -> list[dict]:
    modulos = _modulos(ficha)
    if modulos is None:
        return []
    reglas, disposicion, _, _ = modulos
    return [regla for regla in reglas if disposicion(regla) in ("preliminar", "operacional")]


def definicion_entrada(ficha: FichaDataset, identificador: str) -> dict | None:
    for control in _plantilla(ficha):
        if control["id"] == identificador:
            return control
    return None


def _plantilla(ficha: FichaDataset) -> list[dict]:
    documento = ficha.leer_json("integracion/controles.json")
    if isinstance(documento, dict) and isinstance(documento.get("controles"), list):
        controles = []
        for item in documento["controles"]:
            if not isinstance(item, dict) or not item.get("id"):
                continue
            controles.append({
                "id": item["id"],
                "nombre": item.get("nombre") or item["id"],
                "unidad": item.get("unidad") or "",
                "rol": item.get("rol") or "entrada",
                "via": item.get("via") or "variable",
                "categoria": "entrada_controlable",
                "reglas": [],
                "paso": item.get("paso") or 1,
                "minimo": item.get("minimo"),
                "maximo": item.get("maximo"),
                "leyenda": item.get("leyenda") or "",
                "es_limite_operacional": False,
            })
        if controles:
            return controles
    ejecutables = reglas_ejecutables(ficha)
    if not ejecutables:
        return []
    usadas = []
    for regla in ejecutables:
        for nombre in regla.get("variables_requeridas") or []:
            if nombre in VARIABLES_OPERACIONALES and nombre not in usadas:
                usadas.append(nombre)
    orden = ("frecuencia_hz", "caudal_operacion_bfpd")
    usadas.sort(key=lambda nombre: orden.index(nombre) if nombre in orden else len(orden))
    controles = []
    for nombre in usadas:
        reglas = [regla["id"] for regla in ejecutables if nombre in (regla.get("variables_requeridas") or [])]
        unidad = ejecutables[0]["unidades"].get(nombre)
        for regla in ejecutables:
            if nombre in (regla.get("unidades") or {}):
                unidad = regla["unidades"][nombre]
                break
        controles.append({
            "id": nombre,
            "nombre": NOMBRES.get(nombre, nombre),
            "unidad": unidad,
            "rol": "entrada",
            "via": "variable",
            "categoria": "entrada_controlable",
            "reglas": reglas,
            "paso": 1,
            "es_limite_operacional": False,
        })
    return controles


def controles_de_pozo(pozo: dict, ficha: FichaDataset, frecuencias_escritas: list[float]) -> list[dict]:
    plantilla = _plantilla(ficha)
    if not plantilla:
        return []
    condiciones = pozo.get("condiciones_registradas") if isinstance(pozo.get("condiciones_registradas"), dict) else {}
    dominios = dominios_de(pozo, ficha, _numero(condiciones.get("frecuencia_hz")))
    salida = []
    for base in plantilla:
        valor = _numero(condiciones.get(base["id"]))
        recorrido = dominios.get(base["id"])
        if not recorrido and base.get("minimo") is not None and base.get("maximo") is not None:
            recorrido = {
                "minimo": base["minimo"],
                "maximo": base["maximo"],
                "paso": base.get("paso") or 1,
                "es_limite_operacional": False,
                "leyenda": base.get("leyenda") or "",
            }
        if base["id"] == "frecuencia_hz":
            recorrido = _dominio_frecuencia(valor, frecuencias_escritas)
        salida.append({
            **base,
            "pozo_id": pozo.get("pozo_rotulo"),
            "valor_inicial": valor,
            "valor": valor,
            "habilitado": valor is not None and bool(recorrido) and ficha.puede_evaluar,
            "origen": "observado",
            "procedencia": "condiciones_registradas de la ficha",
            "recorrido": recorrido,
            "convencion": _texto(base["id"], recorrido),
            "motivo_inhabilitado": None if valor is not None else "No está en la medición registrada de este pozo.",
        })
    return salida


def dominios_de(pozo: dict, ficha: FichaDataset, frecuencia: float | None) -> dict:
    """Extremos del caudal: curva tabulada a 60 Hz, llevada con la misma razón que la regla."""
    modulos = _modulos(ficha)
    if modulos is None or frecuencia is None:
        return {}
    _, _, limites_a_frecuencia, base_hz = modulos
    condiciones = pozo.get("condiciones_registradas") if isinstance(pozo.get("condiciones_registradas"), dict) else {}
    qmin = _numero(condiciones.get("limite_minimo_bfpd_a_60hz"))
    qmax = _numero(condiciones.get("limite_maximo_bfpd_a_60hz"))
    curva = [
        _numero(punto.get("caudal_bfpd"))
        for punto in (pozo.get("curva_60hz") or [])
        if isinstance(punto, dict)
    ]
    curva = [valor for valor in curva if valor is not None]
    if qmin is None or qmax is None or not curva:
        return {}
    limites = limites_a_frecuencia({
        "frecuencia_hz": frecuencia,
        "frecuencia_curva_hz": base_hz,
        "limite_minimo_bfpd": qmin,
        "limite_maximo_bfpd": qmax,
    })
    if limites is None:
        return {}
    razon = limites["razon_frecuencia"]
    return {
        "caudal_operacion_bfpd": {
            "minimo": min(curva) * razon,
            "maximo": max(curva) * razon,
            "limite_minimo": limites["minimo_bfpd"],
            "limite_maximo": limites["maximo_bfpd"],
            "paso": 1,
            "es_limite_operacional": False,
            "inclusivo": True,
            "leyenda": (
                "El recorrido es la curva tabulada a 60 Hz, llevada con la misma razón f/f_base de la regla. "
                "Los límites escritos, inclusive, van de "
                f"{limites['minimo_bfpd']} a {limites['maximo_bfpd']} BFPD."
            ),
        }
    }


def _dominio_frecuencia(valor: float | None, frecuencias: list[float]) -> dict | None:
    presentes = [frecuencia for frecuencia in frecuencias if frecuencia is not None]
    if valor is not None:
        presentes.append(valor)
    if not presentes:
        return None
    return {
        "minimo": min(presentes),
        "maximo": max(presentes),
        "paso": 1,
        "es_limite_operacional": False,
        "leyenda": "Extremos: frecuencias escritas en las hojas de este dataset. No son un límite de variador.",
    }


def _texto(identificador: str, recorrido: dict | None) -> str:
    if identificador == "frecuencia_hz":
        return "Entra en RC-BES-01, RC-BES-02 y RC-BES-03 porque los límites de caudal se escalan con Q(f) = Q(60) · f / f_base."
    if identificador == "caudal_operacion_bfpd":
        return "Es el caudal que esas reglas comparan con el mínimo y el máximo escritos."
    return ""


def _numero(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return None
    return float(valor)
