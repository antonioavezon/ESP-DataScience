"""Contratos de entrada y salida del evaluador, y su comprobación.

La comprobación no ejecuta código ajeno: revisa claves, tipos y la prohibición
de recomendar operación sin una regla aprobada para ese uso.
"""

from __future__ import annotations

VERSION_CONTRATO = "1.3.0"
VERSION_MOTOR = "0.4.0"
VERSION_SOFTWARE = "0.4.0"
# 1.3.0 no copia valores sin tipo a la respuesta y admite incidente_id
# más los campos opcionales del error. Una solicitud 1.2.0 queda rechazada.
DATASET_ID = "BES-jun"

# 1.2.0 separa dataset solicitado y dataset evaluado, rechaza variables
# duplicadas y no deja que una medición sobrescriba la ficha del pozo.
# 1.1.0 ya no se acepta: exigía dataset_id constante también en los errores.
# No hay conversión de unidades. Un texto no se convierte a número.
# Un booleano no es una magnitud. Un JSON con claves repetidas no se normaliza.
ESTADOS_EVALUACION = ("completada_preliminar", "no_evaluable", "entrada_invalida", "error_interno")
TIPOS_MENSAJE = (
    "informacion",
    "observacion",
    "advertencia",
    "condicion_no_evaluable",
    "error_dato",
)

# Mediciones que el operador puede enviar en modo operacional.
VARIABLES_OPERACIONALES = frozenset({
    "caudal_operacion_bfpd",
    "frecuencia_hz",
    "presion_sensor_psi",
    "thp_psi",
    "api_deg",
    "bsw_numero",
    "temperatura_c",
})

# Ficha del pozo. En modo operacional no se sustituyen.
# No están validados por existir en el Excel.
PARAMETROS_PROTEGIDOS = frozenset({
    "limite_minimo_bfpd",
    "limite_maximo_bfpd",
    "etapas",
    "id_tubing_in",
    "tvd_descarga_ft",
    "tvd_intake_ft",
    "tvd_sensor_ft",
    "frecuencia_curva_hz",
    "bomba_referencia",
    "curva",
    "cono_eficiencia_bfpd",
})

PARAMETROS_NO_NUMERICOS = frozenset({"bomba_referencia", "curva"})

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
    "cono_eficiencia_bfpd": "BFPD",
}

# Límites de una solicitud externa. Por encima no se recorre el documento.
MAX_CARACTERES_JSON = 100_000
MAX_NODOS = 2_000
MAX_PROFUNDIDAD = 8
MAX_ELEMENTOS = 64
MAX_IDENTIFICADOR = 200


def esquema_entrada() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "bes-jun/contrato_entrada",
        "title": "Solicitud de evaluación BES-jun",
        "type": "object",
        "additionalProperties": False,
        "required": ["dataset_id", "pozo_id", "version_configuracion"],
        "properties": {
            "dataset_id": {"type": "string", "minLength": 1},
            "pozo_id": {"type": "string", "minLength": 1},
            "version_configuracion": {"const": VERSION_CONTRATO},
            "fecha_observacion": {"type": ["string", "null"]},
            "modo": {"enum": ["operacional", "simulacion"]},
            "escenario_id": {"type": ["string", "null"]},
            "configuracion_pozo_id": {"type": ["string", "null"]},
            "parametros_escenario": {"type": "object"},
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
    from reglas.catalogo import VERSION_CATALOGO

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "bes-jun/contrato_salida",
        "title": "Resultado de evaluación BES-jun",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "dataset_solicitado", "dataset_evaluado", "pozo_solicitado", "pozo_resuelto",
            "version_contrato", "version_motor", "version_catalogo_reglas", "version_software",
            "fecha_referencia", "estado_evaluacion", "identidad", "modelos", "reglas",
            "advertencias", "mensajes", "errores", "reglas_ejecutadas",
            "recomendacion_operacional_autorizada", "fuera_de_dominio_observado", "incidente_id",
            "modo", "hipotetico", "escenario_id", "parametros_modificados",
        ],
        "properties": {
            "dataset_solicitado": {"type": "string"},
            "dataset_evaluado": {"type": ["string", "null"], "enum": [DATASET_ID, None]},
            "pozo_solicitado": {"type": "string"},
            "pozo_resuelto": {"type": ["string", "null"]},
            "version_contrato": {"const": VERSION_CONTRATO},
            "version_motor": {"const": VERSION_MOTOR},
            "version_catalogo_reglas": {"const": VERSION_CATALOGO},
            "version_software": {"const": VERSION_SOFTWARE},
            "fecha_referencia": {"type": ["string", "null"]},
            "estado_evaluacion": {"enum": list(ESTADOS_EVALUACION)},
            "identidad": {"type": "object"},
            "modelos": {"type": "array"},
            "reglas": {"type": "array"},
            "advertencias": {"type": "array"},
            "mensajes": {"type": "array"},
            "errores": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["campo", "codigo", "detalle"],
                    "properties": {
                        "campo": {"type": "string"},
                        "codigo": {"type": "string"},
                        "detalle": {"type": "string"},
                        "mensaje": {"type": "string"},
                        "tipo_esperado": {"type": "string"},
                        "unidad_esperada": {"type": "string"},
                    },
                },
            },
            "incidente_id": {"type": ["string", "null"]},
            "reglas_ejecutadas": {"type": "integer", "minimum": 0},
            "recomendacion_operacional_autorizada": {"type": "boolean"},
            "fuera_de_dominio_observado": {"type": "boolean"},
            "modo": {"enum": ["operacional", "simulacion"]},
            "hipotetico": {"type": "boolean"},
            "escenario_id": {"type": ["string", "null"]},
            "parametros_modificados": {"type": "array", "items": {"type": "string"}},
        },
        "allOf": [
            {
                "if": {"properties": {"estado_evaluacion": {"const": "entrada_invalida"}}, "required": ["estado_evaluacion"]},
                "then": {
                    "properties": {
                        "dataset_evaluado": {"type": "null"},
                        "reglas_ejecutadas": {"const": 0},
                        "recomendacion_operacional_autorizada": {"const": False},
                        "modelos": {"maxItems": 0},
                    },
                },
            },
            {
                "if": {"properties": {"estado_evaluacion": {"const": "error_interno"}}, "required": ["estado_evaluacion"]},
                "then": {
                    "properties": {
                        "reglas_ejecutadas": {"const": 0},
                        "recomendacion_operacional_autorizada": {"const": False},
                    },
                },
            },
        ],
    }


# Magnitudes que el modelo ya rechaza si no son estrictamente positivas.
_DEBE_SER_POSITIVA = frozenset({"frecuencia_hz", "id_tubing_in", "etapas", "frecuencia_curva_hz"})
# El modelo rechaza el caudal negativo. El cero no se declara inadmisible aquí.
_NO_PUEDE_SER_NEGATIVA = frozenset({"caudal_operacion_bfpd", "tvd_descarga_ft", "tvd_intake_ft", "tvd_sensor_ft"})


def error_entrada(campo: str, codigo: str, detalle: str, *, tipo_esperado: str | None = None, unidad_esperada: str | None = None) -> dict:
    """Error público. `campo` y `detalle` son siempre texto; no se copia el valor recibido."""
    error = {
        "campo": campo if isinstance(campo, str) and len(campo) <= MAX_IDENTIFICADOR else "(solicitud)",
        "codigo": codigo,
        "detalle": detalle,
        "mensaje": detalle,
    }
    if tipo_esperado:
        error["tipo_esperado"] = tipo_esperado
    if unidad_esperada:
        error["unidad_esperada"] = unidad_esperada
    return error


def excede_estructura(nodo, max_nodos: int = MAX_NODOS, max_prof: int = MAX_PROFUNDIDAD) -> bool:
    """True si el árbol es demasiado profundo, ancho o grande para recorrerlo."""
    pila = [(nodo, 1)]
    vistos = 0
    while pila:
        actual, prof = pila.pop()
        vistos += 1
        if vistos > max_nodos or prof > max_prof:
            return True
        if isinstance(actual, dict):
            if len(actual) > MAX_ELEMENTOS:
                return True
            pila.extend((valor, prof + 1) for valor in actual.values())
        elif isinstance(actual, list):
            if len(actual) > MAX_ELEMENTOS:
                return True
            pila.extend((valor, prof + 1) for valor in actual)
    return False


class _Objeto(dict):
    """Dict que recuerda claves JSON repetidas. El parser estándar se queda con la última."""

    duplicadas: list


def interpretar_json(texto: str):
    """Lee JSON sin descartar claves repetidas.

    Un dict de Python no puede representar dos veces la misma clave. Por eso la
    interfaz que recibe texto usa esta función y rechaza el documento. No elige
    el primer valor ni el último.
    """
    import json

    def pares(items):
        objeto = _Objeto()
        repetidas = []
        for clave, valor in items:
            if clave in objeto:
                repetidas.append(clave)
            objeto[clave] = valor
        objeto.duplicadas = repetidas
        return objeto

    if not isinstance(texto, str):
        return None, [error_entrada("(solicitud)", "TIPO_INVALIDO", "El JSON de entrada es un texto.", tipo_esperado="string")]
    if len(texto) > MAX_CARACTERES_JSON:
        return None, [error_entrada("(solicitud)", "LIMITE_TAMANO", f"El JSON supera {MAX_CARACTERES_JSON} caracteres. No se interpreta.")]
    try:
        documento = json.loads(texto, object_pairs_hook=pares)
    except json.JSONDecodeError as exc:
        return None, [error_entrada("(solicitud)", "ESTRUCTURA_INVALIDA", f"JSON no interpretable: {exc.msg}.")]
    if excede_estructura(documento):
        return None, [error_entrada("(solicitud)", "LIMITE_TAMANO", "La estructura supera el tamaño o la profundidad admitidos. No se recorre.")]
    repetidas = _claves_repetidas(documento)
    if repetidas:
        return None, [
            error_entrada(clave, "CLAVE_JSON_DUPLICADA", "La clave aparece más de una vez en el JSON. No se adopta ningún valor.")
            for clave in repetidas
        ]
    return documento, []


def _claves_repetidas(nodo, camino="") -> list[str]:
    encontradas = []
    if isinstance(nodo, _Objeto):
        for clave in nodo.duplicadas:
            encontradas.append(f"{camino}.{clave}" if camino else clave)
        for clave, valor in nodo.items():
            encontradas.extend(_claves_repetidas(valor, f"{camino}.{clave}" if camino else clave))
    elif isinstance(nodo, list):
        for indice, valor in enumerate(nodo):
            encontradas.extend(_claves_repetidas(valor, f"{camino}[{indice}]"))
    return list(dict.fromkeys(encontradas))


def validar_solicitud(solicitud) -> list[dict]:
    """Esquema, duplicados, parámetros protegidos, unidad y dominio. No calcula."""
    from jsonschema import Draft202012Validator

    if not isinstance(solicitud, dict):
        return [error_entrada("(solicitud)", "ESTRUCTURA_INVALIDA", "La solicitud no es un objeto JSON.", tipo_esperado="object")]
    if excede_estructura(solicitud):
        return [error_entrada("(solicitud)", "LIMITE_TAMANO", "La solicitud supera el tamaño o la profundidad admitidos. No se recorre.")]
    modo = solicitud.get("modo") or "operacional"
    if not isinstance(modo, str):
        modo = "operacional"
    errores = _duplicados_y_proteccion(solicitud.get("variables"), modo)
    errores.extend(_politica_de_modo(solicitud, modo))
    for fallo in Draft202012Validator(esquema_entrada()).iter_errors(solicitud):
        errores.append(_desde_jsonschema(fallo))
    if any(e["codigo"] in ("ESTRUCTURA_INVALIDA", "TIPO_INVALIDO", "CAMPO_OBLIGATORIO", "VERSION_AUSENTE", "VERSION_INCOMPATIBLE", "CAMPO_DESCONOCIDO", "VALOR_NO_ADMITIDO") for e in errores):
        # El resto de la semántica exige una lista de variables bien formada.
        if not isinstance(solicitud.get("variables", []), list):
            return errores
    variables = solicitud.get("variables") or []
    if not isinstance(variables, list):
        return errores
    for indice, item in enumerate(variables):
        if not isinstance(item, dict):
            continue
        nombre = item.get("nombre")
        if not isinstance(nombre, str):
            continue
        campo = f"variables[{indice}].{nombre}"
        if nombre in PARAMETROS_PROTEGIDOS:
            continue
        if nombre not in VARIABLES_OPERACIONALES:
            if not any(e["campo"] == campo and e["codigo"] == "CAMPO_DESCONOCIDO" for e in errores):
                errores.append(error_entrada(campo, "CAMPO_DESCONOCIDO", f"{nombre} no es una medición que este motor acepte."))
            continue
        if item.get("unidad") != UNIDADES_CANONICAS.get(nombre):
            if "unidad" in item and not any(e["campo"] == campo and e["codigo"] == "UNIDAD_INCOMPATIBLE" for e in errores):
                errores.append(error_entrada(
                    campo, "UNIDAD_INCOMPATIBLE",
                    f"Se recibió {item.get('unidad')!r}. La unidad canónica es {UNIDADES_CANONICAS[nombre]!r}. No hay conversión.",
                ))
            continue
        errores.extend(_magnitud(campo, nombre, item.get("valor")))
    if solicitud.get("dataset_id") != DATASET_ID and isinstance(solicitud.get("dataset_id"), str):
        if not any(e["codigo"] == "DATASET_DESCONOCIDO" for e in errores):
            errores.append(error_entrada("dataset_id", "DATASET_DESCONOCIDO", f"Este motor solo evalúa {DATASET_ID}. No se procesó {solicitud.get('dataset_id')!r}."))
    return errores


def validar_sustitucion(entradas, modo: str = "operacional") -> list[dict]:
    """Política del diccionario de ``evaluar``. Un dict de Python no conserva claves duplicadas."""
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
        if clave in PARAMETROS_PROTEGIDOS and modo != "simulacion":
            errores.append(error_entrada(
                clave, "PARAMETRO_PROTEGIDO",
                "Este valor pertenece a la ficha del pozo. Una medición no puede reemplazarlo. "
                "Un escenario hipotético exige modo «simulacion» y un escenario_id.",
            ))
            continue
        if clave in PARAMETROS_NO_NUMERICOS:
            errores.extend(_no_numerico(clave, valor))
            continue
        if clave not in UNIDADES_CANONICAS:
            errores.append(error_entrada(clave, "CAMPO_DESCONOCIDO", f"{clave} no es una variable que este motor sustituya. La solicitud se rechaza."))
            continue
        if clave not in VARIABLES_OPERACIONALES and not (modo == "simulacion" and clave in PARAMETROS_PROTEGIDOS):
            errores.append(error_entrada(clave, "CAMPO_DESCONOCIDO", f"{clave} no es una medición operacional."))
            continue
        if clave not in unidades or unidades[clave] in (None, ""):
            errores.append(error_entrada(clave, "UNIDAD_AUSENTE", f"El contrato {VERSION_CONTRATO} exige la unidad canónica explícita. No se asume."))
            continue
        if unidades[clave] != UNIDADES_CANONICAS[clave]:
            errores.append(error_entrada(
                clave, "UNIDAD_INCOMPATIBLE",
                f"Se recibió {unidades[clave]!r}. La unidad canónica es {UNIDADES_CANONICAS[clave]!r}. No hay conversión.",
            ))
            continue
        errores.extend(_magnitud(clave, clave, valor))
    for clave in unidades:
        if clave not in UNIDADES_CANONICAS and clave not in PARAMETROS_NO_NUMERICOS:
            errores.append(error_entrada(f"unidades.{clave}", "CAMPO_DESCONOCIDO", f"{clave} no es una variable conocida."))
    return errores


def _duplicados_y_proteccion(variables, modo: str) -> list[dict]:
    if variables is None:
        return []
    if not isinstance(variables, list):
        return []
    errores = []
    vistos = {}
    for indice, item in enumerate(variables):
        if not isinstance(item, dict):
            continue
        nombre = item.get("nombre")
        if not isinstance(nombre, str):
            continue
        campo = f"variables[{indice}].{nombre}"
        if nombre in vistos:
            if not any(e["campo"] == nombre and e["codigo"] == "VARIABLE_DUPLICADA" for e in errores):
                errores.append(error_entrada(nombre, "VARIABLE_DUPLICADA", "La variable fue proporcionada más de una vez. No se adopta el primero ni el último."))
        else:
            vistos[nombre] = indice
        if nombre in PARAMETROS_PROTEGIDOS and modo != "simulacion":
            errores.append(error_entrada(
                campo, "PARAMETRO_PROTEGIDO",
                "Este valor pertenece a la ficha del pozo. No se acepta como medición. El límite escrito en el Excel no queda validado por esta negativa.",
            ))
        elif nombre in PARAMETROS_PROTEGIDOS and modo == "simulacion":
            errores.append(error_entrada(
                campo, "PARAMETRO_PROTEGIDO",
                "En simulación el parámetro va en parametros_escenario, no disfrazado de medición.",
            ))
    return errores


def _politica_de_modo(solicitud: dict, modo: str) -> list[dict]:
    errores = []
    if not isinstance(modo, str) or modo not in ("operacional", "simulacion"):
        if "modo" in solicitud:
            errores.append(error_entrada("modo", "VALOR_NO_ADMITIDO", "El modo es «operacional» o «simulacion».", tipo_esperado="string"))
        modo = "operacional"
    escenario = solicitud.get("parametros_escenario")
    if escenario is None:
        escenario = {}
    if not isinstance(escenario, dict):
        errores.append(error_entrada("parametros_escenario", "TIPO_INVALIDO", "Los parámetros del escenario son un objeto.", tipo_esperado="object"))
        escenario = {}
    if modo != "simulacion" and escenario:
        for clave in escenario:
            if not isinstance(clave, str):
                errores.append(error_entrada("parametros_escenario", "TIPO_INVALIDO", "La clave del escenario debe ser texto.", tipo_esperado="string"))
                continue
            errores.append(error_entrada(
                f"parametros_escenario.{clave}", "PARAMETRO_PROTEGIDO",
                "Hay parámetros de escenario sin modo «simulacion». No se aplican.",
            ))
    if modo == "simulacion":
        if not solicitud.get("escenario_id"):
            errores.append(error_entrada("escenario_id", "CAMPO_OBLIGATORIO", "Un escenario hipotético necesita un identificador."))
        if not isinstance(escenario, dict):
            errores.append(error_entrada("parametros_escenario", "TIPO_INVALIDO", "Los parámetros del escenario son un objeto."))
        else:
            for clave, valor in escenario.items():
                if clave not in PARAMETROS_PROTEGIDOS:
                    errores.append(error_entrada(f"parametros_escenario.{clave}", "CAMPO_DESCONOCIDO", f"{clave} no es un parámetro de ficha de este dataset."))
                    continue
                if clave in PARAMETROS_NO_NUMERICOS:
                    errores.extend(_no_numerico(f"parametros_escenario.{clave}", valor))
                    continue
                unidad = valor.get("unidad") if isinstance(valor, dict) else None
                magnitud = valor.get("valor") if isinstance(valor, dict) else valor
                if not isinstance(valor, dict) or unidad != UNIDADES_CANONICAS[clave]:
                    errores.append(error_entrada(
                        f"parametros_escenario.{clave}", "UNIDAD_AUSENTE" if not isinstance(valor, dict) or not unidad else "UNIDAD_INCOMPATIBLE",
                        f"El parámetro de escenario exige la unidad {UNIDADES_CANONICAS[clave]!r}.",
                    ))
                    continue
                errores.extend(_magnitud(f"parametros_escenario.{clave}", clave, magnitud))
    configuracion = solicitud.get("configuracion_pozo_id")
    pozo = solicitud.get("pozo_id")
    if configuracion and pozo and configuracion != pozo:
        errores.append(error_entrada(
            "configuracion_pozo_id", "CONFIGURACION_AJENA",
            "La configuración indicada no es la del pozo solicitado. No se mezcla la ficha de otro pozo.",
        ))
    return errores


def _no_numerico(campo: str, valor) -> list[dict]:
    if campo.endswith("curva") or campo == "curva":
        if not isinstance(valor, list) or not valor:
            return [error_entrada(campo, "TIPO_INVALIDO", "La curva de escenario es una lista de puntos. No sustituye la ficha en modo operacional.")]
        return []
    if not isinstance(valor, str) or not valor.strip():
        return [error_entrada(campo, "TIPO_INVALIDO", "La referencia de bomba del escenario es un texto no vacío.")]
    return []


def _magnitud(campo: str, nombre: str, valor) -> list[dict]:
    if valor is None:
        return [error_entrada(campo, "VALOR_NULO", "Un valor nulo no se evalúa ni se sustituye por el de la hoja.")]
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return [error_entrada(campo, "TIPO_INVALIDO", "Se requiere un valor numérico. No se convierte texto ni booleano.", tipo_esperado="number")]
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
        esperado = fallo.validator_value
        if isinstance(esperado, list):
            esperado = " o ".join(str(parte) for parte in esperado)
        return error_entrada(
            camino, "TIPO_INVALIDO",
            "El tipo no es el del contrato. El valor recibido no se copia a la respuesta.",
            tipo_esperado=str(esperado),
        )
    if fallo.validator == "enum":
        return error_entrada(camino, "VALOR_NO_ADMITIDO", fallo.message)
    return error_entrada(camino, "ESQUEMA", fallo.message)


def errores_de_salida(documento: dict) -> list[str]:
    """Los mismos incumplimientos de esquema que vería un consumidor con el JSON publicado, más la prohibición de recomendar."""
    from jsonschema import Draft202012Validator

    if not isinstance(documento, dict):
        return ["la salida no es un objeto"]
    errores = [f"{fallo.json_path}: {fallo.message}" for fallo in Draft202012Validator(esquema_salida()).iter_errors(documento)]
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
