"""Correspondencia entre el motor y la lámpara de la consola.

Política de esta versión, pendiente de validación técnica: si hay una sola
comparación ejecutable, su resultado es el estado. No se inventa una zona
crítica. ``recomendacion_operacional_autorizada`` no cambia.

- CRÍTICO: regla activa, aprobada para uso operacional y con
  ``limite_critico_validado``. BES-jun no emite esa marca.
- INCIPIENTE: RC-BES-01 o RC-BES-02 activas. Hay un solo umbral escrito
  (por encima del máximo, o por debajo del mínimo). No es un crítico validado.
- NORMAL: RC-BES-03 activa. El caudal queda entre los límites escritos,
  inclusive. Significa que la medición registrada cumple esa comparación.
  No es una autorización de operación.
- Sin una de esas reglas, o si el cálculo falla: no hay lámpara de bomba.
"""

from __future__ import annotations

REGLAS_FUERA_DEL_TEXTO = frozenset({"RC-BES-01", "RC-BES-02"})
REGLAS_DENTRO_DEL_TEXTO = frozenset({"RC-BES-03"})


def clasificar(salida: dict) -> dict:
    estado_motor = salida.get("estado_evaluacion")
    if estado_motor in ("entrada_invalida", "error_interno", "no_disponible"):
        return _sin("ERROR_CALCULO", "CÁLCULO NO COMPLETADO", "No fue posible completar el cálculo.")
    if estado_motor != "completada_preliminar":
        return _sin("SIN_DATOS", "EVALUACIÓN NO DISPONIBLE", "Evaluación no disponible: faltan datos.")

    reglas = [regla for regla in salida.get("reglas") or [] if isinstance(regla, dict)]
    activas = [regla for regla in reglas if regla.get("activada") is True]
    criticas = [regla for regla in activas if _es_critica_validada(regla)]
    if criticas:
        return _operacional(
            "CRITICO", "CRÍTICO", "critico",
            "Una regla aprobada y marcada como límite crítico validado está activa.",
            criticas, "limite_critico_validado",
        )
    if salida.get("recomendacion_operacional_autorizada") is True and _conformidad_aprobada(activas):
        return _operacional(
            "NORMAL", "NORMAL", "normal",
            "Hay una conformidad aprobada para uso operacional y ningún límite crítico validado activo.",
            activas, "conformidad_aprobada",
        )
    incipientes = [regla for regla in activas if _es_alerta_temprana(regla)]
    if incipientes:
        fuera_del_texto = any(regla.get("id") in REGLAS_FUERA_DEL_TEXTO for regla in incipientes)
        return _operacional(
            "INCIPIENTE", "INCIPIENTE", "incipiente",
            "Una regla señala que el caudal queda fuera del límite escrito."
            if fuera_del_texto else
            "Una regla de alerta temprana está activa.",
            incipientes,
            "fuera_del_texto_de_la_hoja" if fuera_del_texto else "alerta_temprana",
        )
    dentro = [regla for regla in activas if regla.get("id") in REGLAS_DENTRO_DEL_TEXTO]
    if dentro:
        return _operacional(
            "NORMAL", "NORMAL", "normal",
            "RC-BES-03: el caudal está entre el mínimo y el máximo escritos, inclusive, a esta frecuencia.",
            dentro, "dentro_de_los_limites_escritos",
        )
    if salida.get("resultados_sin_regla"):
        return _sin(
            "SIN_DATOS",
            "REGISTRO",
            "Hay resultados calculados. Este expediente no define una regla de caudal.",
        )
    if salida.get("fuera_de_dominio_observado"):
        return _sin(
            "SIN_DATOS", "EVALUACIÓN NO DISPONIBLE",
            "La frecuencia sale del dominio observado y no hay una regla de caudal que clasifique el punto.",
            "fuera_del_dominio_observado",
        )
    return _sin(
        "SIN_DATOS", "EVALUACIÓN NO DISPONIBLE",
        "El cálculo terminó sin una regla de caudal que clasifique el punto.",
    )


def _es_critica_validada(regla: dict) -> bool:
    return regla.get("aprobada_para_uso_operacional") is True and regla.get("limite_critico_validado") is True


def _conformidad_aprobada(activas: list[dict]) -> bool:
    return any(
        regla.get("aprobada_para_uso_operacional") is True
        and not _es_critica_validada(regla)
        and (regla.get("id") in REGLAS_DENTRO_DEL_TEXTO or regla.get("conformidad_aprobada") is True)
        for regla in activas
    )


def _es_alerta_temprana(regla: dict) -> bool:
    if _es_critica_validada(regla):
        return False
    return regla.get("id") in REGLAS_FUERA_DEL_TEXTO or regla.get("alerta_temprana") is True


def _operacional(codigo, rotulo, tono, fundamento, reglas, condicion) -> dict:
    ficha = _base(codigo, rotulo, tono, fundamento, True, condicion, reglas)
    return ficha


def _sin(codigo, rotulo, fundamento, condicion: str = "", reglas: list | None = None) -> dict:
    return _base(codigo, rotulo, "sin-clasificacion", fundamento, False, condicion, reglas or [])


def _base(codigo, rotulo, tono, fundamento, valida: bool, condicion: str, reglas: list) -> dict:
    return {
        "codigo": codigo,
        "rotulo": rotulo,
        "tono": tono,
        "clasificacion_valida": valida,
        "condicion": condicion,
        "fundamento": fundamento,
        "reglas": [regla.get("id") for regla in reglas],
        "aprobadas": [regla.get("id") for regla in reglas if regla.get("aprobada_para_uso_operacional") is True],
    }


def respuesta_obsoleta(identificador_recibido: str, identificador_vigente: str) -> bool:
    return identificador_recibido != identificador_vigente
