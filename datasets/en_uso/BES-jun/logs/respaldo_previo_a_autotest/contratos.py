"""Contratos de entrada y salida del evaluador, y su comprobación.

La comprobación no ejecuta código ajeno: revisa claves, tipos y la prohibición
de recomendar operación sin una regla aprobada para ese uso.
"""

from __future__ import annotations

VERSION_CONTRATO = "1.0.0"
DATASET_ID = "BES-jun"

ESTADOS_EVALUACION = ("completada_preliminar", "no_evaluable", "error_validacion")
TIPOS_MENSAJE = (
    "informacion",
    "observacion",
    "advertencia",
    "condicion_no_evaluable",
    "error_dato",
)

UNIDADES_CANONICAS = {
    "caudal_operacion_bfpd": "BFPD",
    "frecuencia_hz": "Hz",
    "presion_sensor_psi": "psi",
    "thp_psi": "psi",
    "id_tubing_in": "in",
    "api_deg": "°API",
    "bsw_numero": "fracción",
    "temperatura_c": "°C",
    "etapas": "1",
    "tvd_descarga_ft": "ft",
    "tvd_intake_ft": "ft",
    "tvd_sensor_ft": "ft",
}


def esquema_entrada() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "bes-jun/contrato_entrada",
        "title": "Solicitud de evaluación BES-jun",
        "type": "object",
        "additionalProperties": False,
        "required": ["dataset_id", "pozo_id", "version_configuracion"],
        "properties": {
            "dataset_id": {"const": DATASET_ID},
            "pozo_id": {"type": "string", "minLength": 1},
            "version_configuracion": {"type": "string"},
            "fecha_observacion": {"type": ["string", "null"]},
            "variables": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["nombre", "valor", "unidad", "procedencia"],
                    "properties": {
                        "nombre": {"type": "string"},
                        "valor": {"type": ["number", "null"]},
                        "unidad": {"type": "string"},
                        "procedencia": {"enum": ["configuracion_del_pozo", "operador", "sensor", "no_declarada"]},
                    },
                },
            },
        },
    }


def esquema_salida() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "bes-jun/contrato_salida",
        "title": "Resultado de evaluación BES-jun",
        "type": "object",
        "required": [
            "dataset_id", "pozo_id", "version_contrato", "version_motor", "estado_evaluacion",
            "identidad", "modelos", "reglas", "advertencias", "mensajes",
            "recomendacion_operacional_autorizada",
        ],
        "properties": {
            "dataset_id": {"const": DATASET_ID},
            "pozo_id": {"type": "string"},
            "version_contrato": {"const": VERSION_CONTRATO},
            "estado_evaluacion": {"enum": list(ESTADOS_EVALUACION)},
            "recomendacion_operacional_autorizada": {"type": "boolean"},
            "reglas": {"type": "array"},
            "advertencias": {"type": "array"},
            "mensajes": {"type": "array"},
        },
    }


def errores_de_salida(documento: dict) -> list[str]:
    """Devuelve mensajes de incumplimiento. Lista vacía si el documento cumple el contrato."""
    errores = []
    for clave in esquema_salida()["required"]:
        if clave not in documento:
            errores.append(f"falta {clave}")
    if documento.get("estado_evaluacion") not in ESTADOS_EVALUACION and "estado_evaluacion" in documento:
        errores.append("estado_evaluacion desconocido")
    reglas = documento.get("reglas") or []
    if not isinstance(reglas, list):
        return errores + ["reglas no es una lista"]
    alguna_aprobada = False
    for regla in reglas:
        if not isinstance(regla, dict):
            errores.append("una regla no es un objeto")
            continue
        for clave in ("id", "estado_regla", "evaluable", "aprobada_para_uso_operacional"):
            if clave not in regla:
                errores.append(f"{regla.get('id', '?')}: falta {clave}")
        if regla.get("aprobada_para_uso_operacional") is True and regla.get("estado_regla") != "aprobada":
            errores.append(f"{regla.get('id')}: marcada como aprobada para operar sin estado «aprobada»")
        if regla.get("aprobada_para_uso_operacional") is True:
            alguna_aprobada = True
        if regla.get("estado_regla") != "aprobada" and regla.get("tipo_mensaje") == "recomendacion_tecnica_validada":
            errores.append(f"{regla.get('id')}: una regla no aprobada emitió recomendación operacional")
    if documento.get("recomendacion_operacional_autorizada") is True and not alguna_aprobada:
        errores.append("recomendacion_operacional_autorizada sin ninguna regla aprobada")
    for mensaje in documento.get("mensajes") or []:
        if isinstance(mensaje, dict) and mensaje.get("tipo") not in TIPOS_MENSAJE:
            errores.append(f"tipo de mensaje no permitido: {mensaje.get('tipo')}")
    return errores
