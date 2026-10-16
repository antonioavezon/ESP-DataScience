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
