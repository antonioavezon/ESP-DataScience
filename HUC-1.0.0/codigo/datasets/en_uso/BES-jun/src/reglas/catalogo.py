"""Catálogo declarativo de las reglas candidatas de BES-jun.

La condición se expresa con operadores de una lista cerrada. No hay código
embebido que el motor ejecute a partir del JSON. La aritmética de los límites
sigue en ``reglas.candidatas_bes_jun`` (una sola implementación).

Ninguna regla de este catálogo está aprobada para uso operacional.
"""

from __future__ import annotations

ESTADOS = (
    "candidata",
    "pendiente_validacion",
    "aprobada",
    "rechazada",
    "suspendida",
    "no_evaluable",
)

OPERADORES = ("mayor_que", "menor_que", "entre_inclusive")

VERSION_CATALOGO = "1.1.0"

REGLAS: tuple[dict, ...] = (
    {
        "id": "RC-BES-01",
        "nombre": "Caudal por encima del máximo escrito, en la misma frecuencia",
        "version": "1.1.0",
        "dataset_origen": "BES-jun",
        "alcance": "hoja de BES-jun con caudal de operación y límites escritos en el bloque de 60 Hz",
        "pozos_aplicables": "los de la hoja evaluada; no es una regla global de otros datasets",
        "familia_bombas": "la referencia escrita en la hoja (S 8000N o S6000N); no es un catálogo de fabricante",
        "descripcion": "Compara el caudal de operación con el límite máximo de la misma hoja, llevado a la frecuencia de operación con Q(f) = Q(60) · f / f_base.",
        "proposito": "Señalar, de forma preliminar, una incoherencia entre el caudal registrado y el máximo escrito.",
        "fundamento_fisico": "La propia hoja escala los caudales de la curva con la frecuencia (afinidad Q ∝ f). Comparar sin escalar mezcla dos bases.",
        "ecuaciones_dependientes": ["F-26-afinidad"],
        "variables_requeridas": ["caudal_operacion_bfpd", "frecuencia_hz", "limite_maximo_bfpd", "frecuencia_curva_hz"],
        "unidades": {"caudal_operacion_bfpd": "BFPD", "frecuencia_hz": "Hz", "limite_maximo_bfpd": "BFPD", "frecuencia_curva_hz": "Hz"},
        "condicion": {"operador": "mayor_que", "izquierda": "caudal_operacion_bfpd", "derecha": "limite_maximo_a_frecuencia_bfpd"},
        "umbral": "celda «Limite maximo», escalada por f/f_base",
        "procedencia_umbral": "texto de la misma hoja; no es un límite de fabricante confirmado",
        "precondiciones": ["caudal, frecuencia y límite máximo presentes", "frecuencia base distinta de cero"],
        "supuestos": ["la relación Q ∝ f de la hoja aplica a este límite", "el caudal y el límite están en BFPD"],
        "dominio": "frecuencia y caudal del punto escrito en la hoja; fuera del rango observado el motor advierte y no aprueba",
        "prioridad": "informativa",
        "estado_validacion": "pendiente_validacion",
        "nivel_confianza": "bajo",
        "aprobada_para_uso_operacional": False,
        "mensaje_si_se_cumple": "El caudal registrado queda por encima del máximo escrito, llevado a la misma frecuencia. Es una observación preliminar: el límite no está aprobado como límite de seguridad.",
        "limitaciones": ["no autoriza cambiar la frecuencia", "el escalamiento no está validado para esta bomba (CT-08)"],
        "consultas_tecnicas": ["CT-06", "CT-08"],
        "responsable_aprobacion": None,
        "fecha_aprobacion": None,
        "funcion_registrada": "reglas.candidatas_bes_jun.comparar_caudal_con_limites",
    },
    {
        "id": "RC-BES-02",
        "nombre": "Caudal por debajo del mínimo escrito, en la misma frecuencia",
        "version": "1.1.0",
        "dataset_origen": "BES-jun",
        "alcance": "igual que RC-BES-01, con el mínimo",
        "pozos_aplicables": "los de la hoja evaluada",
        "familia_bombas": "la referencia escrita en la hoja",
        "descripcion": "Compara el caudal de operación con el límite mínimo escalado a la frecuencia de operación.",
        "proposito": "Señalar, de forma preliminar, un caudal por debajo del mínimo escrito.",
        "fundamento_fisico": "El mismo escalamiento Q ∝ f de la hoja.",
        "ecuaciones_dependientes": ["F-26-afinidad"],
        "variables_requeridas": ["caudal_operacion_bfpd", "frecuencia_hz", "limite_minimo_bfpd", "frecuencia_curva_hz"],
        "unidades": {"caudal_operacion_bfpd": "BFPD", "frecuencia_hz": "Hz", "limite_minimo_bfpd": "BFPD", "frecuencia_curva_hz": "Hz"},
        "condicion": {"operador": "menor_que", "izquierda": "caudal_operacion_bfpd", "derecha": "limite_minimo_a_frecuencia_bfpd"},
        "umbral": "celda «Limite minimo», escalada por f/f_base",
        "procedencia_umbral": "texto de la misma hoja",
        "precondiciones": ["caudal, frecuencia y límite mínimo presentes"],
        "supuestos": ["la relación Q ∝ f aplica al mínimo"],
        "dominio": "el punto escrito en la hoja",
        "prioridad": "informativa",
        "estado_validacion": "pendiente_validacion",
        "nivel_confianza": "bajo",
        "aprobada_para_uso_operacional": False,
        "mensaje_si_se_cumple": "El caudal registrado queda por debajo del mínimo escrito, llevado a la misma frecuencia. Es una observación preliminar.",
        "limitaciones": ["no autoriza cambiar la frecuencia", "en las cinco hojas de BES-jun esta condición no se activa"],
        "consultas_tecnicas": ["CT-06", "CT-08"],
        "responsable_aprobacion": None,
        "fecha_aprobacion": None,
        "funcion_registrada": "reglas.candidatas_bes_jun.comparar_caudal_con_limites",
    },
    {
        "id": "RC-BES-03",
        "nombre": "Caudal dentro de los límites escritos, en la misma frecuencia",
        "version": "1.1.0",
        "dataset_origen": "BES-jun",
        "alcance": "hoja con ambos límites presentes",
        "pozos_aplicables": "los de la hoja evaluada",
        "familia_bombas": "la referencia escrita en la hoja",
        "descripcion": "El caudal de operación está entre el mínimo y el máximo escritos, ambos llevados a la frecuencia de operación. Los extremos inclusive (solo se sale con > máximo o < mínimo).",
        "proposito": "Dejar constancia de coherencia aritmética con los números de la hoja. No es una autorización de operación.",
        "fundamento_fisico": "Misma base de frecuencia que la hoja usa para mover la curva.",
        "ecuaciones_dependientes": ["F-26-afinidad"],
        "variables_requeridas": ["caudal_operacion_bfpd", "frecuencia_hz", "limite_minimo_bfpd", "limite_maximo_bfpd", "frecuencia_curva_hz"],
        "unidades": {"caudal_operacion_bfpd": "BFPD", "frecuencia_hz": "Hz", "limite_minimo_bfpd": "BFPD", "limite_maximo_bfpd": "BFPD"},
        "condicion": {"operador": "entre_inclusive", "valor": "caudal_operacion_bfpd", "minimo": "limite_minimo_a_frecuencia_bfpd", "maximo": "limite_maximo_a_frecuencia_bfpd"},
        "umbral": "celdas «Limite minimo» y «Limite maximo», escaladas",
        "procedencia_umbral": "texto de la misma hoja",
        "precondiciones": ["caudal, frecuencia y ambos límites presentes"],
        "supuestos": ["Q ∝ f aplica a ambos límites"],
        "dominio": "el punto escrito en la hoja",
        "prioridad": "informativa",
        "estado_validacion": "pendiente_validacion",
        "nivel_confianza": "bajo",
        "aprobada_para_uso_operacional": False,
        "mensaje_si_se_cumple": "El caudal registrado queda entre el mínimo y el máximo escritos, en la misma frecuencia. No autoriza operar el pozo.",
        "limitaciones": ["estar entre dos números de la hoja no es un dictamen de seguridad", "CT-08 sigue abierta"],
        "consultas_tecnicas": ["CT-06", "CT-08"],
        "responsable_aprobacion": None,
        "fecha_aprobacion": None,
        "funcion_registrada": "reglas.candidatas_bes_jun.comparar_caudal_con_limites",
    },
    {
        "id": "RC-BES-04",
        "nombre": "Cercanía al punto de máxima eficiencia",
        "version": "1.1.0",
        "dataset_origen": "BES-jun",
        "alcance": "no aplicable con la información de este libro",
        "pozos_aplicables": "ninguno, hasta disponer de curva de fabricante",
        "familia_bombas": "no identificada como catálogo de fabricante",
        "descripcion": "La celda «Cono de eficiencia» coincide con el caudal de mayor EFF de la tabla de seis puntos. No se convirtió en regla de proximidad al BEP.",
        "proposito": "Reservar el identificador y dejar explícito por qué no se evalúa.",
        "fundamento_fisico": "Operar cerca del BEP importa, pero el BEP exige una curva de fabricante y una eficiencia reconciliada. Aquí no están.",
        "ecuaciones_dependientes": [],
        "variables_requeridas": ["cono_eficiencia_bfpd"],
        "unidades": {"cono_eficiencia_bfpd": "BFPD"},
        "condicion": None,
        "umbral": None,
        "procedencia_umbral": "celda «Cono de eficiencia»; no reconciliada con un BEP",
        "precondiciones": ["curva de fabricante identificada", "definición de EFF reconciliada"],
        "supuestos": [],
        "dominio": "ninguno en este expediente",
        "prioridad": "no aplica",
        "estado_validacion": "no_evaluable",
        "nivel_confianza": "ninguno",
        "aprobada_para_uso_operacional": False,
        "mensaje_si_se_cumple": "No evaluable: falta la curva de fabricante y la reconciliación de la columna EFF.",
        "limitaciones": ["no produce verdadero ni falso"],
        "consultas_tecnicas": ["CT-06"],
        "responsable_aprobacion": None,
        "fecha_aprobacion": None,
        "funcion_registrada": None,
    },
)


def disposicion(regla: dict) -> str:
    """Cómo puede usarse el resultado. Solo «operacional» autoriza una recomendación de operación."""
    estado = regla.get("estado_validacion")
    if estado in ("suspendida", "rechazada"):
        return "no_ejecutar"
    if estado == "no_evaluable" or regla.get("condicion") is None:
        return "no_evaluable"
    if estado == "aprobada" and regla.get("aprobada_para_uso_operacional") is True:
        return "operacional"
    return "preliminar"


def por_id(identificador: str) -> dict:
    for regla in REGLAS:
        if regla["id"] == identificador:
            return regla
    raise KeyError(identificador)


def markdown_reglas() -> str:
    """Texto de ``docs/reglas_candidatas.md``. Sale de este catálogo, no de una tabla aparte."""
    lineas = [
        "# Reglas candidatas de BES-jun",
        "",
        f"Versión del catálogo: `{VERSION_CATALOGO}`. Fuente: `src/reglas/catalogo.py`.",
        "La comparación numérica la hace `reglas.candidatas_bes_jun.comparar_caudal_con_limites` (una sola implementación).",
        "",
        "Ninguna regla está aprobada para uso operacional. El resultado es una evaluación preliminar de coherencia",
        "respecto de los números escritos en la hoja, en la misma base de frecuencia.",
        "No autoriza cambiar la frecuencia ni ninguna otra consigna.",
        "",
        "La primera versión comparaba el caudal de operación (a la frecuencia de la hoja) con el límite escrito a 60 Hz.",
        "En QF-084 eso enfrentaba 10 301 BFPD a 63 Hz con 10 000 BFPD a 60 Hz y activaba RC-BES-01.",
        "Con el escalamiento de la propia hoja, Qmax(63 Hz) = 10 000 × 63 / 60 = 10 500 BFPD, y el caudal queda dentro.",
        "Esa corrección aritmética no valida el límite del fabricante ni las leyes de afinidad (CT-08).",
        "`escalar=False` se conserva solo para reproducir el artefacto.",
        "",
    ]
    for regla in REGLAS:
        lineas += [
            f"## {regla['id']}",
            "",
            f"- **Nombre:** {regla['nombre']}",
            f"- **Versión:** {regla['version']}",
            f"- **Estado de validación:** `{regla['estado_validacion']}`",
            f"- **Aprobada para uso operacional:** no" if not regla["aprobada_para_uso_operacional"] else "- **Aprobada para uso operacional:** sí",
            f"- **Confianza:** {regla['nivel_confianza']}",
            f"- **Descripción:** {regla['descripcion']}",
            f"- **Condición:** `{regla['condicion']}`" if regla["condicion"] else "- **Condición:** no evaluable; no hay operador.",
            f"- **Umbral y procedencia:** {regla['umbral']} ({regla['procedencia_umbral']})",
            f"- **Mensaje:** {regla['mensaje_si_se_cumple']}",
            f"- **Limitaciones:** {'; '.join(regla['limitaciones'])}",
            f"- **Consultas:** {', '.join(regla['consultas_tecnicas']) or '—'}",
            f"- **Responsable y fecha de aprobación:** no hay.",
            "",
        ]
    lineas += [
        "## Lo que no se propone",
        "",
        "No se propone subir ni bajar hertz, ni un umbral de sumergencia, ni una comparación con cifras de otros documentos.",
        "",
    ]
    return "\n".join(lineas)
