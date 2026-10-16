"""Modelos M3, M4 y M5 de la fase C, sobre el protocolo 2.14-A.

No cambia los pliegues ni reestima M1 y M2 con otras reglas.
M5 solo predice curvas de gas de mapping cuya curva de agua está en el
entrenamiento y cuyo caudal cae dentro del tramo medido de esa agua.
No rellena los puntos que no puede calcular.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

from esp_datascience.entrenamiento import (
    PrepararEntradas,
    grupos_internos,
    matriz_entradas,
)
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
    SEMILLA,
    agua_utilizable,
    auditar_particiones,
    marcar_pliegues,
)
from esp_datascience.protocolo import CORTES_INTERNOS, N_PLIEGUES_EXTERNOS, VERSION, huella_pliegues

OBJETIVO = "dp2_3_psi"
HUELLAS_PLIEGUES = {
    "mapping": "f35be865a01a6255cc08afdccb96863184ad394a550d9a5249d42b4041a8d948",
    "surging": "71c4818c4b3a5bce0d363c5df658e04141ce1c1301e72f754d5805a52c9dc742",
}
# Fijados antes de ver el error externo. No se busca n_estimators:
# 100 árboles bastan para una semilla fija en estas tablas, y duplicarlos
# no responde otra pregunta científica.
N_ESTIMADORES = 100
PROFUNDIDADES = (3, 5, 7)
HOJAS_MINIMAS = (3, 5, 10)
TOLERANCIA_EMPATE = 1e-9


def _exigir_protocolo(tabla: pd.DataFrame, protocolo: str) -> pd.DataFrame:
    if VERSION != "2.14-A":
        raise RuntimeError(VERSION)
    if protocolo not in HUELLAS_PLIEGUES:
        raise ValueError(protocolo)
    huella = huella_pliegues(tabla, protocolo)
    if huella != HUELLAS_PLIEGUES[protocolo]:
        raise RuntimeError(f"La huella de {protocolo} no es la congelada.")
    auditar_particiones(tabla, protocolo, CORTES_INTERNOS[protocolo])
    return marcar_pliegues(tabla, protocolo)


def _candidatos(protocolo: str) -> tuple[tuple[str, ...], str]:
    if protocolo == "mapping":
        return ("ql_bpd", "velocidad_rpm", "psep_psig"), "ql_bpd"
    return ("gvf0_porcentaje", "velocidad_rpm", "psep_psig"), "gvf0_porcentaje"


def _columnas_ajustables(grupo: pd.DataFrame, protocolo: str) -> list[str]:
    """Predictores que varían dentro de la condición. El que no varía no tiene coeficiente."""
    candidatos, primario = _candidatos(protocolo)
    columnas = [nombre for nombre in candidatos if grupo[nombre].nunique(dropna=True) >= 2]
    if primario not in columnas:
        return []
    if len(grupo) < len(columnas) + 2:
        return []
    return columnas


def factibilidad_m3(tabla: pd.DataFrame, protocolo: str) -> pd.DataFrame:
    """Cuenta curvas por condición, sin ajustar ni mirar la presión objetivo."""
    marcada = _exigir_protocolo(tabla, protocolo)
    filas = []
    for condicion, grupo in marcada.groupby("condicion", sort=True):
        filas.append(_fila_factibilidad(protocolo, condicion, grupo, "global", None, None, grupo))
    for pliegue in range(N_PLIEGUES_EXTERNOS):
        entrena = marcada[marcada["pliegue"] != pliegue]
        prueba = marcada[marcada["pliegue"] == pliegue]
        for condicion, grupo_te in prueba.groupby("condicion", sort=True):
            grupo_tr = entrena[entrena["condicion"] == condicion]
            filas.append(_fila_factibilidad(protocolo, condicion, grupo_tr, "externo", pliegue, None, grupo_te))
        for indice, (_ids_tr, ids_te) in enumerate(grupos_internos(marcada, pliegue, CORTES_INTERNOS[protocolo])):
            interno_tr = entrena[~entrena["curva_id"].isin(ids_te)]
            interno_te = entrena[entrena["curva_id"].isin(ids_te)]
            for condicion, grupo_te in interno_te.groupby("condicion", sort=True):
                grupo_tr = interno_tr[interno_tr["condicion"] == condicion]
                filas.append(
                    _fila_factibilidad(protocolo, condicion, grupo_tr, "interno", pliegue, indice, grupo_te)
                )
    return pd.DataFrame(filas)


def _fila_factibilidad(protocolo, condicion, entrenamiento, alcance, pliegue, interno, prueba) -> dict:
    columnas = _columnas_ajustables(entrenamiento, protocolo) if len(entrenamiento) else []
    presiones_prueba = set(prueba["psep_psig"].unique()) if len(prueba) else set()
    presiones_entrenamiento = set(entrenamiento["psep_psig"].unique()) if len(entrenamiento) else set()
    return {
        "protocolo": protocolo,
        "condicion": condicion,
        "alcance": alcance,
        "pliegue_externo": pliegue,
        "pliegue_interno": interno,
        "n_curvas_entrenamiento": int(entrenamiento["curva_id"].nunique()) if len(entrenamiento) else 0,
        "n_filas_entrenamiento": int(len(entrenamiento)),
        "n_curvas_prueba": int(prueba["curva_id"].nunique()) if len(prueba) else 0,
        "velocidades_entrenamiento": sorted(int(v) for v in entrenamiento["velocidad_rpm"].unique()) if len(entrenamiento) else [],
        "presiones_entrenamiento": sorted(float(v) for v in presiones_entrenamiento),
        "predictores": columnas,
        "estimable": bool(columnas),
        "presiones_de_prueba_ausentes": sorted(float(v) for v in (presiones_prueba - presiones_entrenamiento)),
    }


def evaluar_m3(tabla: pd.DataFrame, protocolo: str) -> dict:
    """Una recta por condición, ajustada solo con las curvas de entrenamiento de esa condición."""
    inicio = time.perf_counter()
    marcada = _exigir_protocolo(tabla, protocolo)
    prediccion = pd.Series(np.nan, index=marcada.index, dtype=float)
    ajuste = pd.Series(np.nan, index=marcada.index, dtype=float)
    extrapolacion = pd.Series(False, index=marcada.index, dtype=bool)
    coeficientes = []
    por_pliegue = []
    for pliegue in range(N_PLIEGUES_EXTERNOS):
        entrena = marcada["pliegue"] != pliegue
        prueba = marcada["pliegue"] == pliegue
        if set(marcada.loc[prueba, "curva_id"]) & set(marcada.loc[entrena, "curva_id"]):
            raise RuntimeError("M3 mezcló una curva de prueba con el entrenamiento.")
        for condicion, grupo_tr in marcada.loc[entrena].groupby("condicion", sort=True):
            columnas = _columnas_ajustables(grupo_tr, protocolo)
            grupo_te = marcada.loc[prueba & marcada["condicion"].eq(condicion)]
            if not columnas or grupo_te.empty:
                continue
            modelo = LinearRegression().fit(grupo_tr[columnas], grupo_tr[OBJETIVO])
            prediccion.loc[grupo_te.index] = modelo.predict(grupo_te[columnas])
            ajuste.loc[grupo_tr.index] = modelo.predict(grupo_tr[columnas])
            presiones = set(grupo_tr["psep_psig"].unique())
            extrapolacion.loc[grupo_te.index] = ~grupo_te["psep_psig"].isin(presiones).to_numpy()
            coeficientes.append(
                {
                    "pliegue": pliegue,
                    "condicion": condicion,
                    "predictores": columnas,
                    "intercepto_psi": float(modelo.intercept_),
                    **{nombre: float(valor) for nombre, valor in zip(columnas, modelo.coef_, strict=True)},
                    "n_curvas_entrenamiento": int(grupo_tr["curva_id"].nunique()),
                }
            )
        por_pliegue.append(_error_de_pliegue(marcada, ajuste, prediccion, entrena, prueba, pliegue))
    predicciones = _marco(marcada, protocolo, prediccion, "prediccion_m3")
    predicciones["extrapolacion_psep_dentro_de_la_condicion"] = extrapolacion.to_numpy()
    paquete = _paquete(protocolo, "M3", predicciones, "prediccion_m3", coeficientes, inicio)
    paquete["errores_por_pliegue"] = pd.DataFrame(por_pliegue)
    return paquete


def pipeline_m4(protocolo: str, max_depth: int, min_samples_leaf: int) -> Pipeline:
    if max_depth not in PROFUNDIDADES or min_samples_leaf not in HOJAS_MINIMAS:
        raise ValueError("El hiperparámetro no está en la rejilla fijada antes de la prueba.")
    return Pipeline(
        [
            ("preparar", PrepararEntradas(protocolo)),
            (
                "bosque",
                RandomForestRegressor(
                    n_estimators=N_ESTIMADORES,
                    max_depth=max_depth,
                    min_samples_leaf=min_samples_leaf,
                    max_features=1.0,
                    random_state=SEMILLA,
                    n_jobs=1,
                ),
            ),
        ]
    )


def elegir_bosque(marcada: pd.DataFrame, protocolo: str, pliegue_externo: int) -> tuple[dict, pd.DataFrame]:
    """Elige profundidad y hoja mínima con el MAE interno. No mira la prueba externa."""
    n_cortes = CORTES_INTERNOS[protocolo]
    filas = []
    for profundidad in PROFUNDIDADES:
        for hoja in HOJAS_MINIMAS:
            medicion, prediccion, curvas = [], [], []
            for ids_tr, ids_te in grupos_internos(marcada, pliegue_externo, n_cortes):
                if ids_te & set(marcada.loc[marcada["pliegue"].eq(pliegue_externo), "curva_id"]):
                    raise RuntimeError("El bosque vio una curva de la prueba externa.")
                mascara_tr = marcada["curva_id"].isin(ids_tr)
                mascara_te = marcada["curva_id"].isin(ids_te)
                modelo = pipeline_m4(protocolo, profundidad, hoja)
                modelo.fit(
                    matriz_entradas(marcada.loc[mascara_tr], protocolo),
                    marcada.loc[mascara_tr, OBJETIVO].to_numpy(dtype=float),
                )
                medicion.append(marcada.loc[mascara_te, OBJETIVO].to_numpy(dtype=float))
                prediccion.append(modelo.predict(matriz_entradas(marcada.loc[mascara_te], protocolo)))
                curvas.append(marcada.loc[mascara_te, "curva_id"].to_numpy())
            mae = media_por_curva(
                np.concatenate(medicion),
                np.concatenate(prediccion),
                np.concatenate(curvas),
                error_absoluto_medio,
            )
            filas.append(
                {
                    "pliegue_externo": int(pliegue_externo),
                    "max_depth": profundidad,
                    "min_samples_leaf": hoja,
                    "n_estimators": N_ESTIMADORES,
                    "mae_interno_por_curva": mae,
                }
            )
    tabla = pd.DataFrame(filas)
    mejor = float(tabla["mae_interno_por_curva"].min())
    candidatos = tabla[tabla["mae_interno_por_curva"] <= mejor + TOLERANCIA_EMPATE]
    candidatos = candidatos.sort_values(["max_depth", "min_samples_leaf"], ascending=[True, False])
    elegido = candidatos.iloc[0]
    return (
        {"max_depth": int(elegido["max_depth"]), "min_samples_leaf": int(elegido["min_samples_leaf"]), "n_estimators": N_ESTIMADORES},
        tabla,
    )


def evaluar_m4(tabla: pd.DataFrame, protocolo: str) -> dict:
    inicio = time.perf_counter()
    marcada = _exigir_protocolo(tabla, protocolo)
    prediccion = pd.Series(np.nan, index=marcada.index, dtype=float)
    busqueda = []
    elegidos = []
    for pliegue in range(N_PLIEGUES_EXTERNOS):
        entrena = marcada["pliegue"] != pliegue
        prueba = marcada["pliegue"] == pliegue
        hiper, detalle = elegir_bosque(marcada, protocolo, pliegue)
        modelo = pipeline_m4(protocolo, hiper["max_depth"], hiper["min_samples_leaf"])
        Xtr = matriz_entradas(marcada.loc[entrena], protocolo)
        modelo.fit(Xtr, marcada.loc[entrena, OBJETIVO].to_numpy(dtype=float))
        yhat_tr = modelo.predict(Xtr)
        yhat_te = modelo.predict(matriz_entradas(marcada.loc[prueba], protocolo))
        prediccion.loc[prueba] = yhat_te
        interno = detalle[
            detalle["max_depth"].eq(hiper["max_depth"]) & detalle["min_samples_leaf"].eq(hiper["min_samples_leaf"])
        ]
        elegidos.append(
            {
                "pliegue": pliegue,
                **hiper,
                "n_filas_entrenamiento": int(entrena.sum()),
                "mae_interno_por_curva": float(interno["mae_interno_por_curva"].iloc[0]),
                "mae_entrenamiento_por_curva": media_por_curva(
                    marcada.loc[entrena, OBJETIVO], yhat_tr, marcada.loc[entrena, "curva_id"], error_absoluto_medio
                ),
                "mae_externo_por_curva": media_por_curva(
                    marcada.loc[prueba, OBJETIVO], yhat_te, marcada.loc[prueba, "curva_id"], error_absoluto_medio
                ),
            }
        )
        busqueda.append(detalle)
    predicciones = _marco(marcada, protocolo, prediccion, "prediccion_m4")
    paquete = _paquete(protocolo, "M4", predicciones, "prediccion_m4", elegidos, inicio)
    paquete["busqueda"] = pd.concat(busqueda, ignore_index=True)
    paquete["hiperparametros"] = pd.DataFrame(elegidos)
    paquete["errores_por_pliegue"] = paquete["hiperparametros"][
        ["pliegue", "mae_interno_por_curva", "mae_entrenamiento_por_curva", "mae_externo_por_curva"]
    ].copy()
    return paquete


def factibilidad_m5(tabla: pd.DataFrame) -> pd.DataFrame:
    """Dice, sin calcular el cociente, qué agua está autorizada en cada pliegue."""
    marcada = _exigir_protocolo(tabla, "mapping")
    relacion = agua_utilizable(marcada)
    filas = []
    for pliegue in range(N_PLIEGUES_EXTERNOS):
        prueba = set(marcada.loc[marcada["pliegue"].eq(pliegue), "curva_id"])
        entrena = set(marcada.loc[marcada["pliegue"].ne(pliegue), "curva_id"])
        gas_prueba = relacion[relacion["curva_id"].isin(prueba)]
        gas_entrena = relacion[relacion["curva_id"].isin(entrena)]
        if set(gas_prueba["curva_agua"]) & prueba:
            raise RuntimeError("Una curva de agua de prueba se usaría para predecir gas de prueba.")
        agua_prueba = marcada[marcada["curva_id"].isin(prueba) & marcada["condicion"].eq("Single Phase")]
        filas.append(
            {
                "pliegue": pliegue,
                "curvas_gas_de_prueba": int(len(gas_prueba)),
                "su_agua_esta_en_entrenamiento": int(gas_prueba["curva_agua"].isin(entrena).sum()),
                "curvas_gas_de_entrenamiento": int(len(gas_entrena)),
                "agua_tambien_en_entrenamiento": int(gas_entrena["curva_agua"].isin(entrena).sum()),
                "agua_reservada_en_la_prueba": int(gas_entrena["curva_agua"].isin(prueba).sum()),
                "curvas_de_agua_en_la_prueba": int(agua_prueba["curva_id"].nunique()),
                "m5_no_predice_el_agua_de_prueba": True,
            }
        )
    return pd.DataFrame(filas)


def evaluar_m5(tabla: pd.DataFrame) -> dict:
    """Cociente respecto del agua de entrenamiento. No es Np y no cubre todas las curvas.

    R = β0 + β1 qgd, ajustada solo en puntos de gas cuyo caudal cae dentro del
    agua autorizada. La predicción en psi es R por la presión de agua interpolada.
    Una curva entra en el MAE solo si todos sus puntos tienen esa interpolación.
    """
    inicio = time.perf_counter()
    marcada = _exigir_protocolo(tabla, "mapping")
    relacion = agua_utilizable(marcada).set_index("curva_id")
    prediccion = pd.Series(np.nan, index=marcada.index, dtype=float)
    coeficientes = []
    for pliegue in range(N_PLIEGUES_EXTERNOS):
        entrena = marcada["pliegue"] != pliegue
        prueba = marcada["pliegue"] == pliegue
        ids_prueba = set(marcada.loc[prueba, "curva_id"])
        ids_entrena = set(marcada.loc[entrena, "curva_id"])
        puntos = _puntos_de_relacion(marcada.loc[entrena], relacion, ids_entrena)
        if puntos.empty or puntos["qgd"].nunique() < 2:
            coeficientes.append({"pliegue": pliegue, "estimable": False, "n_puntos": int(len(puntos))})
            continue
        recta = LinearRegression().fit(puntos[["qgd"]], puntos["relacion"])
        coeficientes.append(
            {
                "pliegue": pliegue,
                "estimable": True,
                "n_puntos": int(len(puntos)),
                "n_curvas_gas": int(puntos["curva_id"].nunique()),
                "intercepto": float(recta.intercept_),
                "pendiente_por_qgd": float(recta.coef_[0]),
            }
        )
        bloque = marcada.loc[prueba & marcada["condicion"].ne("Single Phase")]
        for indice, fila in bloque.iterrows():
            agua_id = relacion.loc[fila["curva_id"], "curva_agua"]
            if agua_id in ids_prueba:
                raise RuntimeError("M5 tomó la curva de agua reservada para la prueba.")
            if agua_id not in ids_entrena:
                continue
            agua = marcada[marcada["curva_id"].eq(agua_id)]
            referencia = _interpolar_agua(agua, float(fila["ql_bpd"]))
            if referencia is None:
                continue
            relacion_predicha = float(recta.intercept_) + float(recta.coef_[0]) * float(fila["qgd"])
            prediccion.loc[indice] = relacion_predicha * referencia
    predicciones = _marco(marcada, "mapping", prediccion, "prediccion_m5")
    paquete = _paquete("mapping", "M5", predicciones, "prediccion_m5", coeficientes, inicio)
    paquete["factibilidad"] = factibilidad_m5(tabla)
    paquete["nota"] = (
        "M5 no compite en todas las curvas. El MAE usa solo las curvas de gas "
        "cuyos caudales caen enteros dentro del agua de entrenamiento."
    )
    return paquete


def _puntos_de_relacion(entrenamiento: pd.DataFrame, relacion: pd.DataFrame, ids_entrena: set[str]) -> pd.DataFrame:
    filas = []
    gas = entrenamiento[entrenamiento["condicion"].ne("Single Phase")]
    for curva, grupo in gas.groupby("curva_id", sort=False):
        agua_id = relacion.loc[curva, "curva_agua"]
        if agua_id not in ids_entrena:
            continue
        agua = entrenamiento[entrenamiento["curva_id"].eq(agua_id)]
        if agua.empty:
            continue
        for _, fila in grupo.iterrows():
            referencia = _interpolar_agua(agua, float(fila["ql_bpd"]))
            if referencia is None or referencia <= 0:
                continue
            filas.append({"curva_id": curva, "qgd": float(fila["qgd"]), "relacion": float(fila[OBJETIVO]) / referencia})
    return pd.DataFrame(filas)


def _interpolar_agua(agua: pd.DataFrame, caudal: float):
    """Interpola dentro del caudal medido. No extrapola."""
    agregado = agua.groupby("ql_bpd", as_index=False)[OBJETIVO].mean().sort_values("ql_bpd")
    xs = agregado["ql_bpd"].to_numpy(dtype=float)
    if caudal < xs[0] or caudal > xs[-1]:
        return None
    return float(np.interp(caudal, xs, agregado[OBJETIVO].to_numpy(dtype=float)))


def metricas_de_columna(predicciones: pd.DataFrame, columna: str, protocolo: str, modelo: str) -> dict:
    """MAE por curva solo en curvas sin huecos. La cobertura queda explícita."""
    incompleta = predicciones.groupby("curva_id")[columna].apply(lambda serie: bool(serie.isna().any()))
    completas = incompleta.index[~incompleta.to_numpy()]
    sub = predicciones[predicciones["curva_id"].isin(completas)]
    cifras = {
        "protocolo": protocolo,
        "modelo": modelo,
        "n_curvas_cubiertas": int(len(completas)),
        "n_curvas_totales": int(predicciones["curva_id"].nunique()),
        "n_filas_cubiertas": int(predicciones[columna].notna().sum()),
        "n_filas_totales": int(len(predicciones)),
    }
    cifras["n_filas_en_el_mae"] = int(len(sub))
    if sub.empty:
        cifras.update(
            {
                "mae_curva": np.nan,
                "rmse_curva": np.nan,
                "sesgo_curva": np.nan,
                "r2_observaciones": np.nan,
                "mae_fila": np.nan,
            }
        )
        return cifras
    y, yhat, curvas = sub["medicion"], sub[columna], sub["curva_id"]
    cifras.update(
        {
            "mae_curva": media_por_curva(y, yhat, curvas, error_absoluto_medio),
            "rmse_curva": media_por_curva(y, yhat, curvas, raiz_error_cuadratico_medio),
            "sesgo_curva": media_por_curva(y, yhat, curvas, sesgo_medio),
            "r2_observaciones": coeficiente_determinacion(y, yhat),
            "mae_fila": error_absoluto_medio(y, yhat),
        }
    )
    return cifras


def diferencias_sobre_curvas_comunes(
    referencia: pd.Series, candidata: pd.Series, exigir_las_mismas: bool = True
) -> pd.Series:
    """Candidata menos referencia. No rellena curvas ausentes."""
    if exigir_las_mismas and not referencia.index.equals(candidata.index):
        raise ValueError("Las curvas no coinciden. La comparación usa los mismos pliegues externos.")
    comunes = referencia.index.intersection(candidata.index)
    if len(comunes) == 0:
        raise ValueError("No hay curvas en común.")
    return diferencia_pareada(referencia.loc[comunes], candidata.loc[comunes])


def _error_de_pliegue(marcada, ajuste, prediccion, entrena, prueba, pliegue) -> dict:
    if ajuste.loc[entrena].isna().any() or prediccion.loc[prueba].isna().any():
        raise RuntimeError(f"El pliegue {pliegue} quedó sin predicción en una curva estimable.")
    return {
        "pliegue": int(pliegue),
        "mae_entrenamiento_por_curva": media_por_curva(
            marcada.loc[entrena, OBJETIVO], ajuste.loc[entrena], marcada.loc[entrena, "curva_id"], error_absoluto_medio
        ),
        "mae_externo_por_curva": media_por_curva(
            marcada.loc[prueba, OBJETIVO], prediccion.loc[prueba], marcada.loc[prueba, "curva_id"], error_absoluto_medio
        ),
    }


def _marco(marcada: pd.DataFrame, protocolo: str, prediccion: pd.Series, columna: str) -> pd.DataFrame:
    if protocolo == "mapping":
        abscisa = marcada["ql_bpd"].to_numpy(dtype=float)
        nombre = "ql_bpd"
    else:
        abscisa = marcada["gvf0_porcentaje"].to_numpy(dtype=float)
        nombre = "gvf0_porcentaje"
    return pd.DataFrame(
        {
            "curva_id": marcada["curva_id"].to_numpy(),
            "pliegue": marcada["pliegue"].to_numpy(dtype=int),
            "hoja": marcada["hoja"].to_numpy(),
            "condicion": marcada["condicion"].to_numpy(),
            "velocidad_rpm": marcada["velocidad_rpm"].to_numpy(dtype=int),
            "psep_psig": marcada["psep_psig"].to_numpy(dtype=float),
            "abscisa": abscisa,
            "abscisa_nombre": nombre,
            "medicion": marcada[OBJETIVO].to_numpy(dtype=float),
            columna: prediccion.to_numpy(dtype=float),
        },
        index=marcada.index,
    )


def _paquete(protocolo, modelo, predicciones, columna, detalle, inicio) -> dict:
    return {
        "protocolo": protocolo,
        "modelo": modelo,
        "version": VERSION,
        "huella": HUELLAS_PLIEGUES[protocolo],
        "predicciones": predicciones,
        "metricas": metricas_de_columna(predicciones, columna, protocolo, modelo),
        "detalle": detalle,
        "mae_por_curva": _mae_por_curva(predicciones, columna),
        "segundos": time.perf_counter() - inicio,
    }


def _mae_por_curva(predicciones: pd.DataFrame, columna: str) -> pd.Series:
    incompleta = predicciones.groupby("curva_id")[columna].apply(lambda serie: bool(serie.isna().any()))
    completas = predicciones[predicciones["curva_id"].isin(incompleta.index[~incompleta.to_numpy()])]
    if completas.empty:
        return pd.Series(dtype=float)
    return metrica_por_curva(completas["medicion"], completas[columna], completas["curva_id"], error_absoluto_medio)


def filas_negativas(predicciones: pd.DataFrame, protocolo: str, modelo: str, columna: str) -> pd.DataFrame:
    """Filas externas con predicción negativa. No sustituye la predicción por cero."""
    limites = predicciones.groupby("curva_id")["abscisa"].agg(abscisa_min="min", abscisa_max="max")
    negativas = predicciones.loc[predicciones[columna] < 0].copy()
    columnas = [
        "protocolo", "modelo", "indice_fila", "curva_id", "pliegue", "hoja",
        "velocidad_rpm", "psep_psig", "condicion", "abscisa_nombre", "abscisa",
        "fraccion_abscisa_en_la_curva", "en_el_extremo_de_la_curva",
        "medicion_psi", "prediccion_psi", "prediccion_menos_medicion_psi", "es_medicion",
    ]
    if negativas.empty:
        return pd.DataFrame(columns=columnas)
    negativas = negativas.join(limites, on="curva_id")
    ancho = (negativas["abscisa_max"] - negativas["abscisa_min"]).replace(0, np.nan)
    fraccion = (negativas["abscisa"] - negativas["abscisa_min"]) / ancho
    filas = []
    for indice, fila in negativas.iterrows():
        fr = float(fraccion.loc[indice])
        prediccion = float(fila[columna])
        medicion = float(fila["medicion"])
        filas.append(
            {
                "protocolo": protocolo,
                "modelo": modelo,
                "indice_fila": int(indice),
                "curva_id": fila["curva_id"],
                "pliegue": int(fila["pliegue"]),
                "hoja": fila["hoja"],
                "velocidad_rpm": int(fila["velocidad_rpm"]),
                "psep_psig": float(fila["psep_psig"]),
                "condicion": fila["condicion"],
                "abscisa_nombre": fila["abscisa_nombre"],
                "abscisa": float(fila["abscisa"]),
                "fraccion_abscisa_en_la_curva": fr,
                "en_el_extremo_de_la_curva": bool(fr <= 0.1 or fr >= 0.9),
                "medicion_psi": medicion,
                "prediccion_psi": prediccion,
                "prediccion_menos_medicion_psi": prediccion - medicion,
                "es_medicion": False,
            }
        )
    return pd.DataFrame(filas, columns=columnas)


def subidas_de_agua(predicciones: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Cuenta pasos que suben en las curvas de agua. No es la correlación de Spearman."""
    agua = predicciones[predicciones["condicion"].eq("Single Phase")]
    filas = []
    for curva, grupo in agua.groupby("curva_id", sort=True):
        if grupo[columna].isna().any():
            filas.append({"curva_id": curva, "subidas_medicion": np.nan, "subidas_modelo": np.nan, "cubierta": False})
            continue
        orden = np.argsort(grupo["abscisa"].to_numpy(dtype=float), kind="mergesort")
        medicion = grupo["medicion"].to_numpy(dtype=float)[orden]
        predicha = grupo[columna].to_numpy(dtype=float)[orden]
        filas.append(
            {
                "curva_id": curva,
                "subidas_medicion": int(np.sum(np.diff(medicion) > 0)),
                "subidas_modelo": int(np.sum(np.diff(predicha) > 0)),
                "cubierta": True,
            }
        )
    return pd.DataFrame(filas)
