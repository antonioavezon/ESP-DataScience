"""Métricas de error en psi. No se aplican a un modelo en la fase A.

El sesgo es predicción menos medición. Un valor positivo dice que el modelo
queda por encima de la medición.
"""

from __future__ import annotations

import numpy as np


def _par(medicion, prediccion):
    y = np.asarray(medicion, dtype=float)
    yhat = np.asarray(prediccion, dtype=float)
    if y.shape != yhat.shape or y.size == 0:
        raise ValueError("Medición y predicción deben tener la misma forma y no estar vacías.")
    if not np.isfinite(y).all() or not np.isfinite(yhat).all():
        raise ValueError("Hay un valor no finito.")
    return y, yhat


def error_absoluto_medio(medicion, prediccion) -> float:
    y, yhat = _par(medicion, prediccion)
    return float(np.mean(np.abs(yhat - y)))


def raiz_error_cuadratico_medio(medicion, prediccion) -> float:
    y, yhat = _par(medicion, prediccion)
    return float(np.sqrt(np.mean((yhat - y) ** 2)))


def sesgo_medio(medicion, prediccion) -> float:
    y, yhat = _par(medicion, prediccion)
    return float(np.mean(yhat - y))


def coeficiente_determinacion(medicion, prediccion) -> float:
    y, yhat = _par(medicion, prediccion)
    centro = float(np.mean(y))
    total = float(np.sum((y - centro) ** 2))
    if total == 0.0:
        raise ValueError("R² no se define si la medición no varía.")
    residuo = float(np.sum((y - yhat) ** 2))
    return float(1.0 - residuo / total)


def metrica_por_curva(medicion, prediccion, curva_id, funcion) -> "pd.Series":
    """Una cifra por curva. Cada curva pesa igual, sin importar cuántos puntos tenga."""
    import pandas as pd

    y, yhat = _par(medicion, prediccion)
    curvas = pd.Series(curva_id).reset_index(drop=True)
    if len(curvas) != len(y) or curvas.isna().any():
        raise ValueError("Cada fila necesita un identificador de curva.")
    tabla = pd.DataFrame({"y": y, "yhat": yhat, "curva": curvas.to_numpy()})
    cifras = {
        curva: float(funcion(grupo["y"].to_numpy(), grupo["yhat"].to_numpy()))
        for curva, grupo in tabla.groupby("curva", sort=True)
    }
    return pd.Series(cifras, name="por_curva")


def media_por_curva(medicion, prediccion, curva_id, funcion) -> float:
    return float(metrica_por_curva(medicion, prediccion, curva_id, funcion).mean())


def diferencia_pareada(serie_referencia, serie_candidata):
    """Resta candidata menos referencia, curva por curva. Exige las mismas curvas."""
    if not serie_referencia.index.equals(serie_candidata.index):
        raise ValueError(
            "Las curvas no coinciden. La comparación usa los mismos pliegues externos."
        )
    return serie_candidata - serie_referencia
