"""Particiones por curvas completas para la actividad 2.14.

No entrena modelos. El pliegue externo no es el GroupKFold de scikit-learn:
ese reparto, sobre estas tablas, deja algún pliegue sin una presión o sin una
fracción de QBEP. Aquí cada curva va a un solo pliegue y cada pliegue de
prueba conserva las dos velocidades, las tres presiones y las condiciones de
gas que el entrenamiento también ve.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

SEMILLA = 214
HOJAS = ("50psig", "100psig", "150psig")
FRACCIONES = ("0.75Qbep", "Qbep", "1.25Qbep")

PREDICTORES_MAPPING = (
    "ql_bpd",
    "es_monofasica",
    "qgd",
    "velocidad_rpm",
    "psep_psig",
)
PREDICTORES_SURGING = (
    "gvf0_porcentaje",
    "fraccion_qbep",
    "velocidad_rpm",
    "psep_psig",
)
# Metadatos de trazabilidad. No entran en la matriz de predictores.
COLUMNAS_PROHIBIDAS = (
    "archivo",
    "hoja",
    "fila",
    "columna_condicion",
    "columna_caudal",
    "columna_dp",
    "columna_gvf",
    "curva_id",
    "origen_velocidad",
    "fila_celda_velocidad",
    "columna_celda_velocidad",
    "valor_celda_velocidad",
    "pliegue",
)


def identificador_curva(tabla: pd.DataFrame) -> pd.Series:
    """Hoja, velocidad y condición. Esa terna es una curva, no un predictor."""
    return (
        tabla["hoja"].astype(str)
        + "|"
        + tabla["velocidad_rpm"].astype(int).astype(str)
        + "|"
        + tabla["condicion"].astype(str)
    )


def pliegue_mapping(hoja: str, velocidad: int, condicion: str) -> int:
    """Tres pliegues. La curva de agua no cae con el gas de su misma hoja y velocidad."""
    indice = HOJAS.index(hoja)
    velocidad_binaria = 0 if int(velocidad) == 1800 else 1
    if condicion == "Single Phase":
        return (indice + velocidad_binaria) % 3
    if condicion == "Qgd=0.01":
        return (indice + velocidad_binaria + 1) % 3
    if condicion == "Qgd=0.005":
        return (indice + 1) % 3
    if condicion == "Qgd=0.015":
        return (indice + 2) % 3
    if condicion in {"Qgd=0.02", "Qgd=0.04"}:
        return indice % 3
    if condicion in {"Qgd=0.03", "Qgd=0.05"}:
        return (indice + 2) % 3
    raise ValueError(f"Condición de mapping no prevista: {condicion}")


def pliegue_surging(hoja: str, condicion: str) -> int:
    """Tres pliegues. Cada fracción de QBEP queda en entrenamiento y en prueba."""
    return (FRACCIONES.index(condicion) - HOJAS.index(hoja)) % 3


def marcar_pliegues(tabla: pd.DataFrame, protocolo: str) -> pd.DataFrame:
    """Copia con curva_id y pliegue. No escribe el CSV."""
    if protocolo not in {"mapping", "surging"}:
        raise ValueError(protocolo)
    copia = tabla.copy()
    copia["curva_id"] = identificador_curva(copia)
    if protocolo == "mapping":
        copia["pliegue"] = [
            pliegue_mapping(hoja, velocidad, condicion)
            for hoja, velocidad, condicion in zip(
                copia["hoja"], copia["velocidad_rpm"], copia["condicion"], strict=True
            )
        ]
    else:
        copia["pliegue"] = [
            pliegue_surging(hoja, condicion)
            for hoja, condicion in zip(copia["hoja"], copia["condicion"], strict=True)
        ]
    return copia


def entradas_mapping(tabla: pd.DataFrame) -> pd.DataFrame:
    """Predictores de mapping. qgd sigue vacío en Single Phase."""
    es_monofasica = (tabla["condicion"] == "Single Phase").to_numpy()
    if not np.array_equal(es_monofasica, tabla["qgd"].isna().to_numpy()):
        raise ValueError("qgd vacío y Single Phase ya no coinciden.")
    entradas = pd.DataFrame(
        {
            "ql_bpd": tabla["ql_bpd"].to_numpy(),
            "es_monofasica": es_monofasica,
            "qgd": tabla["qgd"].to_numpy(),
            "velocidad_rpm": tabla["velocidad_rpm"].to_numpy(),
            "psep_psig": tabla["psep_psig"].to_numpy(),
        }
    )
    if int(entradas.loc[entradas["es_monofasica"], "qgd"].notna().sum()) != 0:
        raise ValueError("Se rellenó qgd en agua.")
    return entradas


def entradas_surging(tabla: pd.DataFrame) -> pd.DataFrame:
    entradas = tabla.loc[:, list(PREDICTORES_SURGING)].copy()
    if entradas.isna().any().any():
        raise ValueError("Surging tiene un predictor vacío.")
    return entradas


def _curvas(tabla_marcada: pd.DataFrame) -> pd.DataFrame:
    return (
        tabla_marcada.groupby("curva_id", sort=False)
        .agg(
            pliegue=("pliegue", "first"),
            n_pliegues=("pliegue", "nunique"),
            hoja=("hoja", "first"),
            velocidad_rpm=("velocidad_rpm", "first"),
            condicion=("condicion", "first"),
            n_filas=("curva_id", "size"),
            origen_velocidad=("origen_velocidad", "first"),
        )
        .reset_index()
    )


def revisar_separacion(curvas: pd.DataFrame, prueba: set[str], entrenamiento: set[str]) -> dict:
    """Comprueba un corte de curvas. No mira los valores de presión."""
    if prueba & entrenamiento:
        fuga = sorted(prueba & entrenamiento)
        raise ValueError(f"Curva en entrenamiento y en prueba: {fuga[0]}")
    sub_prueba = curvas[curvas["curva_id"].isin(prueba)]
    sub_entrenamiento = curvas[curvas["curva_id"].isin(entrenamiento)]
    condiciones_prueba = set(sub_prueba["condicion"])
    condiciones_entrenamiento = set(sub_entrenamiento["condicion"])
    return {
        "n_curvas_prueba": len(prueba),
        "n_curvas_entrenamiento": len(entrenamiento),
        "velocidades_prueba": sorted(int(v) for v in sub_prueba["velocidad_rpm"].unique()),
        "presiones_prueba": sorted(sub_prueba["hoja"].unique()),
        "condiciones_prueba": sorted(condiciones_prueba),
        "condiciones_ausentes_en_entrenamiento": sorted(condiciones_prueba - condiciones_entrenamiento),
        "ambas_velocidades": set(sub_prueba["velocidad_rpm"]) == {1800, 3500},
        "tres_presiones": set(sub_prueba["hoja"]) == set(HOJAS),
        "condiciones_estimables": condiciones_prueba <= condiciones_entrenamiento,
    }


def resumen_pliegues_externos(tabla_marcada: pd.DataFrame) -> pd.DataFrame:
    curvas = _curvas(tabla_marcada)
    if int((curvas["n_pliegues"] != 1).sum()) != 0:
        raise ValueError("Una curva quedó partida entre pliegues.")
    filas = []
    for pliegue, grupo in curvas.groupby("pliegue"):
        prueba = set(grupo["curva_id"])
        entrenamiento = set(curvas.loc[curvas["pliegue"] != pliegue, "curva_id"])
        revision = revisar_separacion(curvas, prueba, entrenamiento)
        filas.append({"pliegue": int(pliegue), "n_filas_prueba": int(grupo["n_filas"].sum()), **revision})
    return pd.DataFrame(filas).sort_values("pliegue").reset_index(drop=True)


def pliegues_internos(tabla_marcada: pd.DataFrame, pliegue_externo: int, n_cortes: int) -> pd.DataFrame:
    """GroupKFold solo sobre las curvas de entrenamiento de un pliegue externo."""
    curvas = _curvas(tabla_marcada)
    entrenamiento = curvas[curvas["pliegue"] != pliegue_externo].reset_index(drop=True)
    grupos = entrenamiento["curva_id"].to_numpy()
    filas = []
    cortes = GroupKFold(n_splits=n_cortes)
    for indice, (_tr, te) in enumerate(cortes.split(np.zeros((len(entrenamiento), 1)), groups=grupos)):
        prueba = set(entrenamiento.iloc[te]["curva_id"])
        resto = set(entrenamiento["curva_id"]) - prueba
        revision = revisar_separacion(entrenamiento, prueba, resto)
        filas.append(
            {
                "pliegue_externo": int(pliegue_externo),
                "pliegue_interno": indice,
                **revision,
            }
        )
    return pd.DataFrame(filas)


def agua_utilizable(tabla_mapping_marcada: pd.DataFrame) -> pd.DataFrame:
    """Para cada curva con gas, dice si su agua de la misma hoja y velocidad está en otro pliegue.

    Sirve para la referencia semiempírica de una fase posterior. No calcula el cociente.
    """
    curvas = _curvas(tabla_mapping_marcada)
    agua = curvas[curvas["condicion"] == "Single Phase"][
        ["hoja", "velocidad_rpm", "pliegue", "curva_id"]
    ].rename(columns={"pliegue": "pliegue_agua", "curva_id": "curva_agua"})
    gas = curvas[curvas["condicion"] != "Single Phase"].merge(agua, on=["hoja", "velocidad_rpm"], how="left")
    if gas["pliegue_agua"].isna().any():
        raise ValueError("Hay una curva con gas sin curva de agua en su hoja y velocidad.")
    gas["agua_en_otro_pliegue"] = gas["pliegue"] != gas["pliegue_agua"]
    return gas
