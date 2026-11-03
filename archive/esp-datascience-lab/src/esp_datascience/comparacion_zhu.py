"""Comparación documental de la actividad 2.15.

No reentrena los modelos de la actividad 2.14 y no implementa una
correlación de Zhu. La puerta numérica no demuestra equivalencia física:
un booleano verdadero no sustituye la lectura de una fuente.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

PARES_NO_EQUIVALENTES = (
    (
        "qgd",
        "gvf0_porcentaje",
        "En la tesis, Qgd es Qg/Qmax y GVF es Qg/(Qg+Ql). No son el mismo número.",
    ),
    (
        "dp2_3_psi",
        "presion_absoluta",
        "dp2_3_psi es un incremento de presión de etapa, no una presión absoluta ni de fondo.",
    ),
    (
        "dp2_3_psi",
        "frontera_de_patron",
        "El artículo de 2019 predice fronteras de patrón de flujo, no el incremento punto a punto.",
    ),
)

CONDICIONES_NUMERICAS = (
    "objetivo_comun",
    "unidades_comunes",
    "protocolo_comun",
    "ecuacion_verificada",
    "datos_disponibles",
    "dominio_conocido",
)

ESTADOS_DE_REGISTRO = ("pendiente", "no_verificada", "citada_en_fuente")
RESULTADOS_DE_REGISTRO = ("cumple", "no_cumple", "sin_dato")

TIPOS_DE_EVIDENCIA = (
    "evidencia experimental original de Zhu",
    "resultado publicado por Zhu",
    "resultado calculado en ESP-DataScience",
    "inferencia del análisis comparativo",
    "hipótesis de investigación futura",
)

COLUMNAS_DE_LA_MATRIZ = (
    "identificador",
    "afirmacion",
    "estudio_o_fuente",
    "documento",
    "pagina_figura_tabla_o_ecuacion",
    "variable",
    "evidencia_disponible",
    "tipo_de_evidencia",
    "grado_de_certeza",
    "comparabilidad",
    "limitacion",
    "interpretacion",
)


@dataclass(frozen=True)
class RegistroCondicion:
    """Una condición de comparación, con fuente aparte del sí o el no.

    `estado="citada_en_fuente"` solo indica que el registro nombra un
    documento. No abre ese documento ni demuestra que dos modelos midan
    lo mismo.
    """

    condicion: str
    resultado: str
    fuente: str
    observaciones: str
    estado: str

    def __post_init__(self) -> None:
        if self.condicion not in CONDICIONES_NUMERICAS:
            raise ValueError(f"Condición desconocida: {self.condicion}")
        if self.resultado not in RESULTADOS_DE_REGISTRO:
            raise ValueError(f"Resultado desconocido: {self.resultado}")
        if self.estado not in ESTADOS_DE_REGISTRO:
            raise ValueError(f"Estado desconocido: {self.estado}")
        if self.estado == "citada_en_fuente" and not self.fuente.strip():
            raise ValueError("Una cita exige una fuente no vacía.")


@dataclass(frozen=True)
class ResultadoPuerta:
    """La puerta administrativa no es una equivalencia física.

    `equivalencia_fisica_demostrada` queda en falso. El constructor
    rechaza el valor verdadero.
    """

    puerta_administrativa: bool
    equivalencia_fisica_demostrada: bool
    motivo: str

    def __post_init__(self) -> None:
        if self.equivalencia_fisica_demostrada:
            raise ValueError(
                "Esta función no puede declarar equivalencia física."
            )


def dossier_de_la_actividad_215() -> tuple[RegistroCondicion, ...]:
    """Registros de esta actividad. Todos dejan la puerta cerrada."""

    nota = (
        "Zhu et al. 2019 predice fronteras de patrón. "
        "La actividad 2.14 predice dp2_3_psi. "
        "La tesis define Qgd y GVF con ecuaciones distintas."
    )
    return tuple(
        RegistroCondicion(
            condicion=nombre,
            resultado="no_cumple",
            fuente="docs/estudio_comparativo_zhu_2_15.md, sección 5",
            observaciones=nota,
            estado="citada_en_fuente",
        )
        for nombre in CONDICIONES_NUMERICAS
    )


def exigir_comparacion_numerica(registros) -> ResultadoPuerta:
    """Deja pasar solo una lista completa de registros citados que cumplen.

    No acepta booleanos. Aunque la puerta administrativa quede abierta,
    la equivalencia física permanece en falso: esta función no lee la
    fuente ni calcula un error.
    """

    if isinstance(registros, bool) or not isinstance(registros, (list, tuple)):
        raise TypeError(
            "Un valor booleano no verifica una condición. "
            "Hace falta una lista de RegistroCondicion con fuente."
        )
    if any(isinstance(item, bool) for item in registros):
        raise TypeError(
            "Un valor booleano no verifica una condición. "
            "Hace falta una lista de RegistroCondicion con fuente."
        )
    vistos = []
    for item in registros:
        if not isinstance(item, RegistroCondicion):
            raise TypeError(
                "Cada condición debe ser un RegistroCondicion, no un booleano."
            )
        vistos.append(item.condicion)
    if tuple(vistos) != CONDICIONES_NUMERICAS and set(vistos) != set(CONDICIONES_NUMERICAS):
        raise ValueError("Faltan condiciones del listado obligatorio.")
    if len(vistos) != len(CONDICIONES_NUMERICAS):
        raise ValueError("Hay condiciones repetidas o ausentes.")
    bloqueos = [
        item.condicion
        for item in registros
        if item.resultado != "cumple" or item.estado != "citada_en_fuente"
    ]
    if bloqueos:
        raise ValueError(
            "Comparación numérica no defendible. "
            "Sin cita y cumplimiento: " + ", ".join(bloqueos)
        )
    return ResultadoPuerta(
        puerta_administrativa=True,
        equivalencia_fisica_demostrada=False,
        motivo=(
            "La puerta administrativa se abrió porque cada registro cita una fuente "
            "y declara cumplimiento. Eso no demuestra equivalencia física ni calcula un error."
        ),
    )


def auditar_matriz(ruta: Path) -> dict:
    """Rechaza identificadores duplicados, celdas vacías o tipos desconocidos."""

    with Path(ruta).open(encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames is None:
            raise ValueError("La matriz no tiene encabezado.")
        if tuple(lector.fieldnames) != COLUMNAS_DE_LA_MATRIZ:
            raise ValueError("La matriz no tiene las columnas esperadas.")
        filas = list(lector)
    vistos = []
    for fila in filas:
        identificador = (fila.get("identificador") or "").strip()
        if not identificador:
            raise ValueError("Hay una fila sin identificador.")
        if identificador in vistos:
            raise ValueError(f"Identificador duplicado: {identificador}")
        vistos.append(identificador)
        for columna in COLUMNAS_DE_LA_MATRIZ:
            if not (fila.get(columna) or "").strip():
                raise ValueError(f"{identificador} tiene vacía la columna {columna}.")
        tipo = fila["tipo_de_evidencia"].strip()
        if tipo not in TIPOS_DE_EVIDENCIA:
            raise ValueError(f"Tipo de evidencia desconocido en {identificador}: {tipo}")
    return {"filas": len(filas), "identificadores": tuple(vistos)}
