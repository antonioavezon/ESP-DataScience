"""Reglas congeladas de la actividad 2.14 antes del primer entrenamiento.

No ajusta modelos. Si una fase posterior cambia un pliegue, la métrica principal
o el tratamiento de Qgd, ese cambio es una modificación metodológica: hay que
escribir la justificación y decir qué comparaciones dejan de ser válidas.
"""

from __future__ import annotations

import hashlib

import pandas as pd

from esp_datascience.particiones import (
    HOJAS,
    identificador_curva,
    marcar_pliegues,
)

VERSION = "2.14-A"
CONGELADO = True
ALCANCE = (
    "Predicción de curvas nuevas dentro del dominio ya medido: la velocidad, "
    "la presión del separador y la condición de la curva de prueba aparecen en "
    "otras curvas del entrenamiento. No demuestra que el modelo valga en una "
    "velocidad, una presión o una condición de gas que el entrenamiento no vio."
)
METRICA_PRINCIPAL = "MAE en psi, media no ponderada del MAE de cada curva de prueba"
METRICAS_COMPLEMENTARIAS = (
    "RMSE en psi, media no ponderada por curva",
    "sesgo en psi, predicción menos medición, media no ponderada por curva",
)
COMPARACION = "pareada, sobre los mismos pliegues externos"
CORTES_INTERNOS = {"mapping": 4, "surging": 3}
N_PLIEGUES_EXTERNOS = 3

# Cómo entra cada variable a los modelos M1 y M2. M3 usa la condición como factor.
TRATAMIENTO = {
    "mapping": {
        "ql_bpd": "numérica, caudal de líquido en bpd",
        "es_monofasica": "indicador de agua; no es una medición de gas",
        "qgd": "numérica y ausente en agua; el CSV no se rellena",
        "qgd_tecnico": "cero solo dentro del pipeline cuando es agua; no es un Qgd medido",
        "velocidad_rpm": "numérica ordenada, 1800 o 3500; no se parte en variables ficticias",
        "psep_psig": "numérica ordenada, 50, 100 o 150; no se parte en variables ficticias",
        "condicion": "categórica, solo para la recta por condición",
    },
    "surging": {
        "gvf0_porcentaje": "numérica continua; es el gas",
        "fraccion_qbep": "numérica ordenada en M1 y M2; factor en la recta por bloque",
        "velocidad_rpm": "numérica ordenada, 1800 o 3500",
        "psep_psig": "numérica ordenada, 50, 100 o 150",
    },
}


def huella_pliegues(tabla: pd.DataFrame, protocolo: str) -> str:
    """Huella del reparto externo. Cambia solo si cambia la asignación de una curva."""
    marcada = marcar_pliegues(tabla, protocolo)
    curvas = (
        marcada.groupby("curva_id", sort=True)["pliegue"].first().astype(int)
    )
    texto = "\n".join(f"{curva}|{pliegue}" for curva, pliegue in curvas.items())
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def condiciones_no_vistas(tabla: pd.DataFrame, protocolo: str) -> pd.DataFrame:
    """Describe, sin ejecutar, una reserva de etiquetas completas.

    No sustituye los tres pliegues principales. No devuelve índices de ajuste.
    """
    if protocolo not in {"mapping", "surging"}:
        raise ValueError(protocolo)
    trabajo = tabla.copy()
    trabajo["curva_id"] = identificador_curva(trabajo)
    columnas = {
        "condicion": ("condicion", "first"),
        "velocidad_rpm": ("velocidad_rpm", "first"),
        "hoja": ("hoja", "first"),
    }
    if protocolo == "mapping":
        columnas["qgd"] = ("qgd", "first")
        valor = "qgd"
        que_prueba = "condición de gas no vista"
    else:
        columnas["fraccion_qbep"] = ("fraccion_qbep", "first")
        valor = "fraccion_qbep"
        que_prueba = "fracción de QBEP no vista; no es un GVF0 no visto"
    curvas = trabajo.groupby("curva_id", sort=False).agg(**columnas).reset_index()
    numeros = {}
    for condicion, grupo in curvas.groupby("condicion"):
        presentes = grupo[valor].dropna().unique()
        numeros[condicion] = None if len(presentes) == 0 else float(presentes[0])
    filas = []
    for condicion, grupo in curvas.groupby("condicion", sort=True):
        propio = numeros[condicion]
        otros = [numero for etiqueta, numero in numeros.items() if etiqueta != condicion and numero is not None]
        if propio is None:
            posicion = "sin valor numérico de gas"
        elif not otros:
            posicion = "sin otros valores"
        elif min(otros) < propio < max(otros):
            posicion = "entre otros valores del archivo"
        else:
            posicion = "en el borde de los valores del archivo"
        filas.append(
            {
                "protocolo": protocolo,
                "etiqueta_reservada": condicion,
                "n_curvas": int(grupo["curva_id"].nunique()),
                "velocidades": sorted(int(v) for v in grupo["velocidad_rpm"].unique()),
                "hojas": sorted(grupo["hoja"].unique()),
                "que_probaria": que_prueba,
                "posicion_numerica": posicion,
                "la_recta_por_etiqueta_puede_predecirla": False,
                "es_la_evaluacion_principal": False,
                "ejecutada": False,
            }
        )
    informe = pd.DataFrame(filas)
    if set(informe["hojas"].map(lambda hojas: set(hojas) == set(HOJAS))) != {True}:
        raise ValueError("Una etiqueta no está en las tres presiones.")
    return informe
