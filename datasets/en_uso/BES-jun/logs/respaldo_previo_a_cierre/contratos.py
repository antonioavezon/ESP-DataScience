"""Contratos de entrada y salida del evaluador, y su comprobación.

La comprobación no ejecuta código ajeno: revisa claves, tipos y la prohibición
de recomendar operación sin una regla aprobada para ese uso.
"""

from __future__ import annotations

VERSION_CONTRATO = "1.1.0"
DATASET_ID = "BES-jun"

# 1.1.0 añade «entrada_invalida»: la solicitud no pasa el esquema, la unidad,
# el tipo o el dominio físico, y no se ejecuta ningún modelo.
# No hay conversión de unidades: solo se acepta la unidad canónica.
# Un texto no se convierte a número. Un booleano no es una magnitud.
ESTADOS_EVALUACION = ("completada_preliminar", "no_evaluable", "error_validacion", "entrada_invalida")
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
    "frecuencia_curva_hz": "Hz",
    "limite_minimo_bfpd": "BFPD",
    "limite_maximo_bfpd": "BFPD",
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
            "version_configuracion": {"const": VERSION_CONTRATO},
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
                        "unidad": {"type": "string", "minLength": 1},
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
            "identidad", "modelos", "reglas", "advertencias", "mensajes", "errores",
            "reglas_ejecutadas", "recomendacion_operacional_autorizada",
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


# Magnitudes que el modelo ya rechaza si no son estrictamente positivas.
_DEBE_SER_POSITIVA = frozenset({"frecuencia_hz", "id_tubing_in", "etapas", "frecuencia_curva_hz"})
# El modelo rechaza el caudal negativo. El cero no se declara inadmisible aquí.
_NO_PUEDE_SER_NEGATIVA = frozenset({"caudal_operacion_bfpd", "tvd_descarga_ft", "tvd_intake_ft", "tvd_sensor_ft"})


def error_entrada(campo: str, codigo: str, detalle: str) -> dict:
    return {"campo": campo, "codigo": codigo, "detalle": detalle}


def validar_solicitud(solicitud) -> list[dict]:
    """Esquema JSON (jsonschema) y, si pasa, unidad canónica y dominio físico.

    No ejecuta modelos. No convierte textos ni unidades.
    """
    from jsonschema import Draft202012Validator

    if not isinstance(solicitud, dict):
        return [error_entrada("(solicitud)", "ESTRUCTURA_INVALIDA", "La solicitud no es un objeto JSON.")]
    errores = []
    for fallo in Draft202012Validator(esquema_entrada()).iter_errors(solicitud):
        errores.append(_desde_jsonschema(fallo))
    if errores:
        return errores
    for indice, item in enumerate(solicitud.get("variables") or []):
        campo = f"variables[{indice}].{item.get('nombre', '')}"
        nombre = item["nombre"]
        if nombre not in UNIDADES_CANONICAS:
            errores.append(error_entrada(campo, "CAMPO_DESCONOCIDO", f"{nombre} no es una variable que este motor acepte."))
            continue
        if item["unidad"] != UNIDADES_CANONICAS[nombre]:
            errores.append(error_entrada(
                campo, "UNIDAD_INCOMPATIBLE",
                f"Se recibió {item['unidad']!r}. La unidad canónica es {UNIDADES_CANONICAS[nombre]!r}. No hay conversión.",
            ))
            continue
        errores.extend(_magnitud(campo, nombre, item["valor"]))
    return errores


def validar_sustitucion(entradas) -> list[dict]:
    """Misma política para el diccionario que acepta ``evaluar`` además de la solicitud JSON."""
    if entradas is None:
        return []
    if not isinstance(entradas, dict):
        return [error_entrada("entradas", "ESTRUCTURA_INVALIDA", "Las entradas no son un objeto.")]
    unidades = entradas.get("unidades", {})
    if not isinstance(unidades, dict):
        return [error_entrada("unidades", "TIPO_INVALIDO", "Las unidades deben ser un objeto nombre → unidad.")]
    errores = []
    for clave, valor in entradas.items():
        if clave == "unidades":
            continue
        if clave not in UNIDADES_CANONICAS:
            errores.append(error_entrada(clave, "CAMPO_DESCONOCIDO", f"{clave} no es una variable que este motor sustituya. La solicitud se rechaza."))
            continue
        if clave not in unidades or unidades[clave] in (None, ""):
            errores.append(error_entrada(clave, "UNIDAD_AUSENTE", "El contrato 1.1.0 exige la unidad canónica explícita. No se asume."))
            continue
        if unidades[clave] != UNIDADES_CANONICAS[clave]:
            errores.append(error_entrada(
                clave, "UNIDAD_INCOMPATIBLE",
                f"Se recibió {unidades[clave]!r}. La unidad canónica es {UNIDADES_CANONICAS[clave]!r}. No hay conversión.",
            ))
            continue
        errores.extend(_magnitud(clave, clave, valor))
    for clave in unidades:
        if clave not in UNIDADES_CANONICAS:
            errores.append(error_entrada(f"unidades.{clave}", "CAMPO_DESCONOCIDO", f"{clave} no es una variable conocida."))
    return errores


def _magnitud(campo: str, nombre: str, valor) -> list[dict]:
    if valor is None:
        return [error_entrada(campo, "VALOR_NULO", "Un valor nulo no se evalúa ni se sustituye por el de la hoja.")]
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return [error_entrada(campo, "TIPO_INVALIDO", "Se requiere un valor numérico. No se convierte texto ni booleano.")]
    if valor != valor or valor in (float("inf"), float("-inf")):
        return [error_entrada(campo, "VALOR_NO_FINITO", "Infinito y NaN no son magnitudes de entrada.")]
    if nombre in _DEBE_SER_POSITIVA and valor <= 0:
        return [error_entrada(campo, "FISICAMENTE_INADMISIBLE", f"{nombre} debe ser mayor que cero. No es un límite operacional: es el dominio de la fórmula.")]
    if nombre in _NO_PUEDE_SER_NEGATIVA and valor < 0:
        return [error_entrada(campo, "FISICAMENTE_INADMISIBLE", f"{nombre} no puede ser negativo.")]
    return []


def _desde_jsonschema(fallo) -> dict:
    camino = ".".join(str(parte) for parte in fallo.absolute_path) or "(solicitud)"
    if fallo.validator == "required":
        faltante = fallo.message.split("'")[1] if "'" in fallo.message else camino
        codigo = "VERSION_AUSENTE" if faltante == "version_configuracion" else "CAMPO_OBLIGATORIO"
        return error_entrada(faltante, codigo, fallo.message)
    if fallo.validator == "additionalProperties":
        return error_entrada(camino or "(solicitud)", "CAMPO_DESCONOCIDO", fallo.message)
    if fallo.validator == "const" and (camino == "dataset_id" or camino.endswith("dataset_id")):
        return error_entrada("dataset_id", "DATASET_DESCONOCIDO", fallo.message)
    if fallo.validator == "const" and "version_configuracion" in camino:
        return error_entrada("version_configuracion", "VERSION_INCOMPATIBLE", f"Este motor usa el contrato {VERSION_CONTRATO}.")
    if fallo.validator == "minLength":
        codigo = "VERSION_AUSENTE" if "version" in camino else "IDENTIFICADOR_MAL_FORMADO"
        return error_entrada(camino, codigo, fallo.message)
    if fallo.validator == "type":
        return error_entrada(camino, "TIPO_INVALIDO", fallo.message)
    if fallo.validator == "enum":
        return error_entrada(camino, "VALOR_NO_ADMITIDO", fallo.message)
    return error_entrada(camino, "ESQUEMA", fallo.message)


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
    if documento.get("estado_evaluacion") == "entrada_invalida":
        if not documento.get("errores"):
            errores.append("entrada_invalida sin lista de errores")
        if documento.get("reglas_ejecutadas") not in (0, None) and documento.get("reglas_ejecutadas") != 0:
            errores.append("entrada_invalida ejecutó reglas")
    if "reglas_ejecutadas" in documento and not isinstance(documento["reglas_ejecutadas"], int):
        errores.append("reglas_ejecutadas no es un entero")
    for mensaje in documento.get("mensajes") or []:
        if isinstance(mensaje, dict) and mensaje.get("tipo") not in TIPOS_MENSAJE:
            errores.append(f"tipo de mensaje no permitido: {mensaje.get('tipo')}")
    return errores
