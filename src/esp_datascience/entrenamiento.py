"""Entrenamiento de M1 y M2 con la validación anidada de la versión 2.14-A.

M1 es la regresión lineal. M2 es el polinomio de grado 2 con cresta.
No estima la recta por condición, el bosque ni el cociente de agua.
No escribe los CSV ni cambia el pliegue de ninguna curva.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

from esp_datascience.metricas import (
    coeficiente_determinacion,
    diferencia_pareada,
    error_absoluto_medio,
    media_por_curva,
    metrica_por_curva,
    raiz_error_cuadratico_medio,
    sesgo_medio,
)
from esp_datascience.particiones import (
    COLUMNAS_PROHIBIDAS,
    auditar_particiones,
    entradas_mapping,
    entradas_surging,
    marcar_pliegues,
    pliegues_internos,
)
from esp_datascience.protocolo import CORTES_INTERNOS, N_PLIEGUES_EXTERNOS, VERSION, huella_pliegues

OBJETIVO = "dp2_3_psi"
GRADO_POLINOMIO = 2
ALPHAS = (0.01, 0.1, 1.0, 10.0, 100.0)
TOLERANCIA_EMPATE_ALPHA = 1e-9
HUELLAS_PLIEGUES = {
    "mapping": "f35be865a01a6255cc08afdccb96863184ad394a550d9a5249d42b4041a8d948",
    "surging": "71c4818c4b3a5bce0d363c5df658e04141ce1c1301e72f754d5805a52c9dc742",
}
ORDEN_M1 = ("preparar", "linea")
ORDEN_M2 = ("preparar", "polinomio", "columnas_estructurales", "escala", "cresta")


class PrepararEntradas(BaseEstimator, TransformerMixin):
    """Arma la matriz numérica. En mapping, el cero de Qgd vive solo en la copia."""

    def __init__(self, protocolo: str = "mapping"):
        self.protocolo = protocolo

    def fit(self, X, y=None):
        if self.protocolo not in {"mapping", "surging"}:
            raise ValueError(self.protocolo)
        marco = self._marco(X)
        self.nombres_salida_ = (
            ("ql_bpd", "es_monofasica", "qgd_tecnico", "velocidad_rpm", "psep_psig")
            if self.protocolo == "mapping"
            else ("gvf0_porcentaje", "fraccion_qbep", "velocidad_rpm", "psep_psig")
        )
        self.n_features_in_ = marco.shape[1]
        if any(nombre in COLUMNAS_PROHIBIDAS for nombre in self.nombres_salida_):
            raise RuntimeError("Un predictor prohibido entró en la matriz.")
        return self

    def transform(self, X):
        marco = self._marco(X)
        if self.protocolo == "mapping":
            from esp_datascience.particiones import qgd_tecnico

            ausencias = int(marco["qgd"].isna().sum())
            tecnico = qgd_tecnico(marco["qgd"], marco["es_monofasica"])
            if int(marco["qgd"].isna().sum()) != ausencias:
                raise RuntimeError("La preparación modificó qgd.")
            columnas = [
                marco["ql_bpd"].to_numpy(dtype=float),
                marco["es_monofasica"].to_numpy(dtype=float),
                tecnico.to_numpy(dtype=float),
                marco["velocidad_rpm"].to_numpy(dtype=float),
                marco["psep_psig"].to_numpy(dtype=float),
            ]
        else:
            columnas = [marco[nombre].to_numpy(dtype=float) for nombre in self.nombres_salida_]
        matriz = np.column_stack(columnas)
        if not np.isfinite(matriz).all():
            raise ValueError("La matriz de predictores tiene un valor no finito.")
        return matriz

    def _marco(self, X) -> pd.DataFrame:
        if not isinstance(X, pd.DataFrame):
            raise TypeError("Las entradas tienen que llegar con nombre de columna.")
        if self.protocolo == "mapping":
            return entradas_mapping(X) if "condicion" in X.columns else X.copy()
        return entradas_surging(X) if "gvf0_porcentaje" in X.columns and set(entradas_surging(X).columns) <= set(X.columns) else X.copy()


class ColumnasEstructurales(BaseEstimator, TransformerMixin):
    """Quita columnas idénticamente nulas. No usa la presión ni la prueba externa."""

    def fit(self, X, y=None):
        matriz = np.asarray(X, dtype=float)
        self.soporte_ = np.ptp(matriz, axis=0) > 0.0
        if int(self.soporte_.sum()) == 0:
            raise ValueError("Todas las columnas del polinomio quedaron nulas.")
        self.n_features_in_ = matriz.shape[1]
        return self

    def transform(self, X):
        return np.asarray(X, dtype=float)[:, self.soporte_]


def matriz_entradas(tabla: pd.DataFrame, protocolo: str) -> pd.DataFrame:
    """Copia de predictores. No incluye identificadores ni el origen de la velocidad."""
    if protocolo == "mapping":
        entradas = entradas_mapping(tabla)
        entradas.insert(0, "condicion", tabla["condicion"].to_numpy())
        return entradas
    return entradas_surging(tabla)


def pipeline_m1(protocolo: str) -> Pipeline:
    return Pipeline(
        [
            ("preparar", PrepararEntradas(protocolo)),
            ("linea", LinearRegression()),
        ]
    )


def pipeline_m2(protocolo: str, alpha: float) -> Pipeline:
    alpha_fijo = _alpha_de_rejilla(alpha)
    return Pipeline(
        [
            ("preparar", PrepararEntradas(protocolo)),
            (
                "polinomio",
                PolynomialFeatures(degree=GRADO_POLINOMIO, include_bias=False),
            ),
            ("columnas_estructurales", ColumnasEstructurales()),
            ("escala", StandardScaler()),
            ("cresta", Ridge(alpha=alpha_fijo, fit_intercept=True, solver="svd")),
        ]
    )


def _alpha_de_rejilla(alpha: float) -> float:
    for candidato in ALPHAS:
        if math.isclose(float(alpha), float(candidato), rel_tol=0.0, abs_tol=0.0):
            return float(candidato)
    raise ValueError(f"Alpha {alpha} no está en la rejilla fijada antes de la prueba.")


def grupos_internos(marcada: pd.DataFrame, pliegue_externo: int, n_cortes: int) -> list[tuple[set[str], set[str]]]:
    """Mismos cortes que pliegues_internos: curvas completas del entrenamiento externo."""
    orden = (
        marcada.groupby("curva_id", sort=False)
        .agg(pliegue=("pliegue", "first"))
        .reset_index()
    )
    entrenamiento = orden[orden["pliegue"] != pliegue_externo].reset_index(drop=True)
    prueba_externa = set(orden.loc[orden["pliegue"] == pliegue_externo, "curva_id"])
    grupos = entrenamiento["curva_id"].to_numpy()
    from sklearn.model_selection import GroupKFold

    cortes = []
    vistos: set[str] = set()
    for _tr, te in GroupKFold(n_splits=n_cortes).split(np.zeros((len(entrenamiento), 1)), groups=grupos):
        ids_te = set(entrenamiento.iloc[te]["curva_id"])
        ids_tr = set(entrenamiento["curva_id"]) - ids_te
        if ids_te & prueba_externa or ids_tr & prueba_externa:
            raise RuntimeError("El anillo interno tomó una curva de la prueba externa.")
        if ids_te & ids_tr or vistos & ids_te:
            raise RuntimeError("Una curva interna quedó repetida o mezclada.")
        vistos |= ids_te
        cortes.append((ids_tr, ids_te))
    if vistos != set(entrenamiento["curva_id"]):
        raise RuntimeError("El anillo interno no recorre el entrenamiento.")
    informe = pliegues_internos(marcada, pliegue_externo, n_cortes)
    if list(informe["n_curvas_prueba"]) != [len(ids_te) for _ids_tr, ids_te in cortes]:
        raise RuntimeError("Los cortes internos no coinciden con la fase A.")
    return cortes


def elegir_alpha(marcada: pd.DataFrame, protocolo: str, pliegue_externo: int) -> tuple[float, pd.DataFrame]:
    """Elige alpha por el MAE interno de las curvas de entrenamiento. No mira la prueba."""
    n_cortes = CORTES_INTERNOS[protocolo]
    filas = []
    for alpha in ALPHAS:
        medicion = []
        prediccion = []
        curvas = []
        for ids_tr, ids_te in grupos_internos(marcada, pliegue_externo, n_cortes):
            mascara_tr = marcada["curva_id"].isin(ids_tr)
            mascara_te = marcada["curva_id"].isin(ids_te)
            if int((marcada.loc[mascara_te, "pliegue"] == pliegue_externo).sum()) != 0:
                raise RuntimeError("Alpha vio una fila de la prueba externa.")
            modelo = pipeline_m2(protocolo, alpha)
            Xtr = matriz_entradas(marcada.loc[mascara_tr], protocolo)
            ytr = marcada.loc[mascara_tr, OBJETIVO].to_numpy(dtype=float)
            modelo.fit(Xtr, ytr)
            if int(modelo.named_steps["escala"].n_samples_seen_) != len(Xtr):
                raise RuntimeError("La escala no se ajustó solo con el entrenamiento interno.")
            medicion.append(marcada.loc[mascara_te, OBJETIVO].to_numpy(dtype=float))
            prediccion.append(modelo.predict(matriz_entradas(marcada.loc[mascara_te], protocolo)))
            curvas.append(marcada.loc[mascara_te, "curva_id"].to_numpy())
        mae = media_por_curva(
            np.concatenate(medicion),
            np.concatenate(prediccion),
            np.concatenate(curvas),
            error_absoluto_medio,
        )
        filas.append({"pliegue_externo": int(pliegue_externo), "alpha": float(alpha), "mae_interno_por_curva": mae})
    tabla = pd.DataFrame(filas)
    mejor = float(tabla["mae_interno_por_curva"].min())
    candidatos = tabla[tabla["mae_interno_por_curva"] <= mejor + TOLERANCIA_EMPATE_ALPHA]
    elegido = float(candidatos["alpha"].max())
    return _alpha_de_rejilla(elegido), tabla


def _cifras(medicion, prediccion, curvas) -> dict:
    return {
        "mae_fila": error_absoluto_medio(medicion, prediccion),
        "mae_curva": media_por_curva(medicion, prediccion, curvas, error_absoluto_medio),
        "rmse_curva": media_por_curva(medicion, prediccion, curvas, raiz_error_cuadratico_medio),
        "rmse_fila": raiz_error_cuadratico_medio(medicion, prediccion),
        "sesgo_curva": media_por_curva(medicion, prediccion, curvas, sesgo_medio),
        "sesgo_fila": sesgo_medio(medicion, prediccion),
        "r2_observaciones": coeficiente_determinacion(medicion, prediccion),
    }


def evaluar_protocolo(tabla: pd.DataFrame, protocolo: str) -> dict:
    """Tres pliegues externos congelados. Cada fila recibe una predicción externa por modelo."""
    if VERSION != "2.14-A":
        raise RuntimeError(f"La versión del protocolo ya no es 2.14-A: {VERSION}")
    if protocolo not in HUELLAS_PLIEGUES:
        raise ValueError(protocolo)
    huella = huella_pliegues(tabla, protocolo)
    if huella != HUELLAS_PLIEGUES[protocolo]:
        raise RuntimeError(f"La huella de {protocolo} no es la congelada.")
    auditoria = auditar_particiones(tabla, protocolo, CORTES_INTERNOS[protocolo])
    marcada = marcar_pliegues(tabla, protocolo)
    if protocolo == "mapping" and int(tabla["qgd"].isna().sum()) != int(marcada["qgd"].isna().sum()):
        raise RuntimeError("Marcar los pliegues alteró qgd.")
    prediccion_m1 = pd.Series(np.nan, index=marcada.index, dtype=float)
    prediccion_m2 = pd.Series(np.nan, index=marcada.index, dtype=float)
    alphas = []
    busqueda = []
    entrenamiento = []
    coeficientes = []
    for pliegue in range(N_PLIEGUES_EXTERNOS):
        prueba = marcada["pliegue"] == pliegue
        entrena = ~prueba
        if set(marcada.loc[prueba, "curva_id"]) & set(marcada.loc[entrena, "curva_id"]):
            raise RuntimeError("Una curva está en los dos lados del pliegue externo.")
        Xtr = matriz_entradas(marcada.loc[entrena], protocolo)
        ytr = marcada.loc[entrena, OBJETIVO].to_numpy(dtype=float)
        curvas_tr = marcada.loc[entrena, "curva_id"].to_numpy()
        Xte = matriz_entradas(marcada.loc[prueba], protocolo)
        m1 = pipeline_m1(protocolo)
        m1.fit(Xtr, ytr)
        pred_te_m1 = m1.predict(Xte)
        pred_tr_m1 = m1.predict(Xtr)
        alpha, detalle = elegir_alpha(marcada, protocolo, pliegue)
        m2 = pipeline_m2(protocolo, alpha)
        m2.fit(Xtr, ytr)
        if int(m2.named_steps["escala"].n_samples_seen_) != int(entrena.sum()):
            raise RuntimeError("La escala final usó filas que no son del entrenamiento externo.")
        if tuple(m2.named_steps) != ORDEN_M2:
            raise RuntimeError("Cambió el orden de las transformaciones de M2.")
        nulas = int((~m2.named_steps["columnas_estructurales"].soporte_).sum())
        if nulas != (1 if protocolo == "mapping" else 0):
            raise RuntimeError("Apareció una columna nula que no es el producto estructural de mapping.")
        pred_te_m2 = m2.predict(Xte)
        pred_tr_m2 = m2.predict(Xtr)
        prediccion_m1.loc[prueba] = pred_te_m1
        prediccion_m2.loc[prueba] = pred_te_m2
        alphas.append({"pliegue": pliegue, "alpha": alpha, "n_filas_entrenamiento": int(entrena.sum()), "n_filas_prueba": int(prueba.sum())})
        busqueda.append(detalle)
        for modelo, pred_tr, pred_te in (
            ("M1", pred_tr_m1, pred_te_m1),
            ("M2", pred_tr_m2, pred_te_m2),
        ):
            cifras_tr = _cifras(ytr, pred_tr, curvas_tr)
            cifras_te = _cifras(
                marcada.loc[prueba, OBJETIVO].to_numpy(dtype=float),
                pred_te,
                marcada.loc[prueba, "curva_id"].to_numpy(),
            )
            entrenamiento.append({"pliegue": pliegue, "modelo": modelo, "mae_curva_entrenamiento": cifras_tr["mae_curva"], "mae_curva_externo": cifras_te["mae_curva"]})
        nombres = m1.named_steps["preparar"].nombres_salida_
        coeficientes.append(
            {
                "pliegue": pliegue,
                "intercepto_psi": float(m1.named_steps["linea"].intercept_),
                **{nombre: float(valor) for nombre, valor in zip(nombres, m1.named_steps["linea"].coef_, strict=True)},
            }
        )
    if prediccion_m1.isna().any() or prediccion_m2.isna().any():
        raise RuntimeError("Quedó una fila sin predicción externa.")
    predicciones = _predicciones(marcada, protocolo, prediccion_m1, prediccion_m2)
    externo = _tabla_externa(predicciones, protocolo)
    diferencias = _diferencias(predicciones)
    return {
        "protocolo": protocolo,
        "version": VERSION,
        "huella": huella,
        "auditoria": auditoria,
        "predicciones": predicciones,
        "externo": externo,
        "entrenamiento": pd.DataFrame(entrenamiento),
        "alphas": pd.DataFrame(alphas),
        "busqueda_alpha": pd.concat(busqueda, ignore_index=True),
        "coeficientes_m1": pd.DataFrame(coeficientes),
        "diferencias": diferencias,
        "desglose": _desglose(predicciones),
        "ejemplos": _ejemplos(diferencias),
        "fisico": diagnostico_fisico(predicciones, protocolo),
    }


def _predicciones(marcada, protocolo, prediccion_m1, prediccion_m2) -> pd.DataFrame:
    if protocolo == "mapping":
        abscisa = marcada["ql_bpd"].to_numpy(dtype=float)
        abscisa_nombre = "ql_bpd"
    else:
        abscisa = marcada["gvf0_porcentaje"].to_numpy(dtype=float)
        abscisa_nombre = "gvf0_porcentaje"
    return pd.DataFrame(
        {
            "curva_id": marcada["curva_id"].to_numpy(),
            "pliegue": marcada["pliegue"].to_numpy(dtype=int),
            "hoja": marcada["hoja"].to_numpy(),
            "condicion": marcada["condicion"].to_numpy(),
            "velocidad_rpm": marcada["velocidad_rpm"].to_numpy(dtype=int),
            "psep_psig": marcada["psep_psig"].to_numpy(dtype=float),
            "abscisa": abscisa,
            "abscisa_nombre": abscisa_nombre,
            "medicion": marcada[OBJETIVO].to_numpy(dtype=float),
            "prediccion_m1": prediccion_m1.to_numpy(dtype=float),
            "prediccion_m2": prediccion_m2.to_numpy(dtype=float),
        },
        index=marcada.index,
    )


def _tabla_externa(predicciones: pd.DataFrame, protocolo: str) -> pd.DataFrame:
    filas = []
    for modelo, columna in (("M1", "prediccion_m1"), ("M2", "prediccion_m2")):
        cifras = _cifras(predicciones["medicion"], predicciones[columna], predicciones["curva_id"])
        filas.append({"protocolo": protocolo, "modelo": modelo, **cifras})
    return pd.DataFrame(filas)


def _diferencias(predicciones: pd.DataFrame) -> pd.DataFrame:
    mae_m1 = metrica_por_curva(predicciones["medicion"], predicciones["prediccion_m1"], predicciones["curva_id"], error_absoluto_medio)
    mae_m2 = metrica_por_curva(predicciones["medicion"], predicciones["prediccion_m2"], predicciones["curva_id"], error_absoluto_medio)
    delta = diferencia_pareada(mae_m1, mae_m2)
    meta = (
        predicciones.groupby("curva_id", sort=True)
        .agg(
            pliegue=("pliegue", "first"),
            hoja=("hoja", "first"),
            condicion=("condicion", "first"),
            velocidad_rpm=("velocidad_rpm", "first"),
            psep_psig=("psep_psig", "first"),
            n_puntos=("medicion", "size"),
        )
    )
    return meta.assign(mae_m1=mae_m1, mae_m2=mae_m2, delta_mae=delta).reset_index()


def _desglose(predicciones: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for modelo, columna in (("M1", "prediccion_m1"), ("M2", "prediccion_m2")):
        for factor in ("velocidad_rpm", "psep_psig", "condicion"):
            for nivel, grupo in predicciones.groupby(factor, sort=True):
                cifras = _cifras(grupo["medicion"], grupo[columna], grupo["curva_id"])
                filas.append(
                    {
                        "modelo": modelo,
                        "factor": factor,
                        "nivel": nivel,
                        "n_curvas": int(grupo["curva_id"].nunique()),
                        "mae_curva": cifras["mae_curva"],
                        "sesgo_curva": cifras["sesgo_curva"],
                    }
                )
    return pd.DataFrame(filas)


def _ejemplos(diferencias: pd.DataFrame) -> dict:
    """Curvas de las figuras, elegidas solo con el MAE de M1.

    Por velocidad, la curva más cercana a la mediana de esa velocidad.
    Además, la curva con el mayor MAE de M1 en todo el protocolo.
    """
    serie = diferencias.set_index("curva_id")["mae_m1"]
    velocidades = diferencias.set_index("curva_id")["velocidad_rpm"]

    def cercana(subconjunto: pd.Series) -> str:
        mediana = float(subconjunto.median())
        return str((subconjunto - mediana).abs().idxmin())

    return {
        "tipica_1800": cercana(serie[velocidades.eq(1800)]),
        "tipica_3500": cercana(serie[velocidades.eq(3500)]),
        "dificil": str(serie.idxmax()),
        "mediana_mae_m1": float(serie.median()),
    }


def diagnostico_fisico(predicciones: pd.DataFrame, protocolo: str) -> dict:
    """Describe la forma predicha. No impone una restricción ni descarta un modelo."""
    resumen = {
        "predicciones_negativas_m1": int((predicciones["prediccion_m1"] < 0).sum()),
        "predicciones_negativas_m2": int((predicciones["prediccion_m2"] < 0).sum()),
        "mediciones_negativas": int((predicciones["medicion"] < 0).sum()),
        "min_prediccion_m1": float(predicciones["prediccion_m1"].min()),
        "min_prediccion_m2": float(predicciones["prediccion_m2"].min()),
        "min_medicion": float(predicciones["medicion"].min()),
        "max_prediccion_m1": float(predicciones["prediccion_m1"].max()),
        "max_prediccion_m2": float(predicciones["prediccion_m2"].max()),
        "max_medicion": float(predicciones["medicion"].max()),
    }
    por_velocidad = (
        predicciones.groupby(["curva_id", "velocidad_rpm"], sort=False)
        .agg(medicion=("medicion", "mean"), m1=("prediccion_m1", "mean"), m2=("prediccion_m2", "mean"))
        .reset_index()
        .groupby("velocidad_rpm")[["medicion", "m1", "m2"]]
        .mean()
    )
    resumen["media_por_velocidad"] = por_velocidad
    if protocolo == "mapping":
        resumen["gas"] = _pasos_de_gas(predicciones)
        resumen["agua"] = _monotonia_agua(predicciones)
    else:
        resumen["gas"] = _asociacion_gvf(predicciones)
    return resumen


def _pasos_de_gas(predicciones: pd.DataFrame) -> pd.DataFrame:
    """Entre curvas de la misma hoja y velocidad, ordenadas por el Qgd medido. El agua no entra."""
    curvas = (
        predicciones.groupby("curva_id", sort=False)
        .agg(
            hoja=("hoja", "first"),
            velocidad_rpm=("velocidad_rpm", "first"),
            condicion=("condicion", "first"),
            medicion=("medicion", "mean"),
            m1=("prediccion_m1", "mean"),
            m2=("prediccion_m2", "mean"),
        )
        .reset_index()
    )
    curvas = curvas[curvas["condicion"] != "Single Phase"].copy()
    curvas["qgd"] = curvas["condicion"].str.replace("Qgd=", "", regex=False).astype(float)
    filas = []
    for (hoja, velocidad), grupo in curvas.groupby(["hoja", "velocidad_rpm"], sort=True):
        grupo = grupo.sort_values("qgd")
        for modelo, columna in (("medicion", "medicion"), ("M1", "m1"), ("M2", "m2")):
            pasos = np.diff(grupo[columna].to_numpy(dtype=float))
            filas.append(
                {
                    "hoja": hoja,
                    "velocidad_rpm": int(velocidad),
                    "modelo": modelo,
                    "pasos": int(len(pasos)),
                    "pasos_en_que_sube": int(np.sum(pasos > 0)),
                }
            )
    return pd.DataFrame(filas)


def _monotonia_agua(predicciones: pd.DataFrame) -> pd.DataFrame:
    """En las curvas de agua, el caudal es la abscisa. La medición baja al subir el caudal."""
    from scipy.stats import spearmanr

    agua = predicciones[predicciones["condicion"].eq("Single Phase")]
    filas = []
    for curva, grupo in agua.groupby("curva_id", sort=True):
        filas.append(
            {
                "curva_id": curva,
                "medicion": float(spearmanr(grupo["abscisa"], grupo["medicion"]).statistic),
                "M1": float(spearmanr(grupo["abscisa"], grupo["prediccion_m1"]).statistic),
                "M2": float(spearmanr(grupo["abscisa"], grupo["prediccion_m2"]).statistic),
            }
        )
    return pd.DataFrame(filas)


def _asociacion_gvf(predicciones: pd.DataFrame) -> pd.DataFrame:
    """Dentro de cada curva de surging, asociación entre GVF0 y el incremento de presión."""
    from scipy.stats import spearmanr

    filas = []
    for curva, grupo in predicciones.groupby("curva_id", sort=True):
        fila = {"curva_id": curva, "n_puntos": int(len(grupo))}
        for nombre, columna in (("medicion", "medicion"), ("M1", "prediccion_m1"), ("M2", "prediccion_m2")):
            fila[nombre] = float(spearmanr(grupo["abscisa"], grupo[columna]).statistic)
        filas.append(fila)
    return pd.DataFrame(filas)


def tabla_comparativa(resultados: list[dict]) -> pd.DataFrame:
    """MAE, RMSE y sesgo con igual peso por curva. R² es el de las observaciones externas."""
    tabla = pd.concat([resultado["externo"] for resultado in resultados], ignore_index=True)
    return tabla.loc[:, ["protocolo", "modelo", "mae_curva", "rmse_curva", "sesgo_curva", "r2_observaciones", "mae_fila"]].copy()


def repetir_es_identico(tabla: pd.DataFrame, protocolo: str) -> bool:
    primera = evaluar_protocolo(tabla, protocolo)
    segunda = evaluar_protocolo(tabla, protocolo)
    return bool(
        np.allclose(primera["predicciones"]["prediccion_m1"], segunda["predicciones"]["prediccion_m1"])
        and np.allclose(primera["predicciones"]["prediccion_m2"], segunda["predicciones"]["prediccion_m2"])
        and primera["alphas"]["alpha"].equals(segunda["alphas"]["alpha"])
    )


def clonar_para_prueba(modelo: Pipeline) -> Pipeline:
    """El clon no hereda la escala ya ajustada."""
    return clone(modelo)
