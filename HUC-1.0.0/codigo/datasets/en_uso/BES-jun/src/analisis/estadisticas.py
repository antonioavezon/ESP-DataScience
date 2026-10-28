"""Estadística descriptiva. Un punto de operación no es una serie temporal."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from ingesta.leer_bes_jun import raiz_expediente
from ingesta.survey import leer_survey

CAMPOS_OPERACION = (
    ("caudal_operacion_bfpd", "BFPD"),
    ("presion_sensor_psi", "psi"),
    ("thp_psi", "psi"),
    ("cache_pip_ft", "ft"),
    ("cache_thd_ft", "ft"),
    ("frecuencia_hz", "Hz"),
)

CAMPOS_SURVEY = (
    ("md_ft", "ft"),
    ("inclinacion_deg", "deg"),
    ("azimut_deg", "deg"),
    ("vertical_ft", "ft"),
    ("dogleg_deg_por_100ft", "deg/100ft"),
)


def describir(valores: list[float | None]) -> dict:
    faltantes = sum(v is None for v in valores)
    datos = [float(v) for v in valores if isinstance(v, (int, float))]
    n = len(datos)
    vacio = {
        "n": n,
        "faltantes": faltantes,
        "minimo": None,
        "maximo": None,
        "media": None,
        "mediana": None,
        "desviacion_estandar": None,
        "p05": None,
        "p25": None,
        "p75": None,
        "p95": None,
    }
    if n == 0:
        return vacio
    arr = np.asarray(datos, dtype=float)
    vacio.update(
        {
            "minimo": float(arr.min()),
            "maximo": float(arr.max()),
            "media": float(arr.mean()),
            "mediana": float(np.median(arr)),
            "desviacion_estandar": float(arr.std(ddof=1)) if n > 1 else None,
            "p05": float(np.percentile(arr, 5)),
            "p25": float(np.percentile(arr, 25)),
            "p75": float(np.percentile(arr, 75)),
            "p95": float(np.percentile(arr, 95)),
        }
    )
    return vacio


def tabla_operacion(hojas: list[dict]) -> list[dict]:
    filas = []
    for hoja in hojas:
        for campo, unidad in CAMPOS_OPERACION:
            stats = describir([hoja.get(campo)])
            filas.append(
                {
                    "hoja": hoja.get("hoja"),
                    "pozo": hoja.get("pozo"),
                    "variable": campo,
                    "unidad": unidad,
                    "alcance": "un punto de operacion de esta hoja",
                    **stats,
                }
            )
    return filas


def tabla_survey(estaciones: list[dict]) -> list[dict]:
    hojas = []
    for estacion in estaciones:
        if estacion["hoja"] not in hojas:
            hojas.append(estacion["hoja"])
    filas = []
    for hoja in hojas:
        grupo = [e for e in estaciones if e["hoja"] == hoja]
        for campo, unidad in CAMPOS_SURVEY:
            stats = describir([e[campo] for e in grupo])
            pasos = _pasos([e["md_ft"] for e in grupo])
            filas.append(
                {
                    "hoja": hoja,
                    "variable": campo,
                    "unidad": unidad,
                    "alcance": "estaciones Measured de esta hoja",
                    "paso_md_mediana_ft": pasos["mediana"] if campo == "md_ft" else None,
                    "paso_md_minimo_ft": pasos["minimo"] if campo == "md_ft" else None,
                    "paso_md_maximo_ft": pasos["maximo"] if campo == "md_ft" else None,
                    **stats,
                }
            )
    return filas


def _pasos(profundidades: list[float]) -> dict:
    if len(profundidades) < 2:
        return {"mediana": None, "minimo": None, "maximo": None}
    difs = np.diff(np.asarray(profundidades, dtype=float))
    return {
        "mediana": float(np.median(difs)),
        "minimo": float(difs.min()),
        "maximo": float(difs.max()),
    }


def guardar_tablas(hojas: list[dict], estaciones: list[dict] | None = None) -> dict[str, Path]:
    raiz = raiz_expediente()
    destino = raiz / "data_procesados"
    destino.mkdir(parents=True, exist_ok=True)
    if estaciones is None:
        estaciones = leer_survey()
    operacion = tabla_operacion(hojas)
    survey = tabla_survey(estaciones)
    ruta_op = destino / "estadisticas_operacion.csv"
    ruta_sv = destino / "estadisticas_survey.csv"
    ruta_est = destino / "survey_estaciones.csv"
    _csv(ruta_op, operacion)
    _csv(ruta_sv, survey)
    _csv(ruta_est, estaciones)
    nota = destino / "transformaciones.md"
    nota.write_text(
        "\n".join(
            [
                "# Transformaciones",
                "",
                "No se borró, corrigió ni imputó ningún valor del Excel.",
                "La copia de trabajo no se guardó desde openpyxl.",
                "`survey_estaciones.csv` copia las filas numéricas del bloque `Measured`.",
                "Se omitió la fila de unidades que sigue al encabezado (`Depth (ft)`).",
                "Cada hoja queda identificada por su nombre. No se unieron pozos.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {"operacion": ruta_op, "survey": ruta_sv, "estaciones": ruta_est, "nota": nota}


def _csv(ruta: Path, filas: list[dict]) -> None:
    if not filas:
        ruta.write_text("", encoding="utf-8")
        return
    campos = list(filas[0].keys())
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)
