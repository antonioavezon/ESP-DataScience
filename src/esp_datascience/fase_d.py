"""Comparación e incertidumbre de la fase D.

No reajusta M1–M5 ni cambia el protocolo 2.14-A.
La semilla y el número de réplicas quedan fijados aquí, antes de leer un intervalo.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon

from esp_datascience.metricas import (
    diferencia_pareada,
    error_absoluto_medio,
    metrica_por_curva,
    sesgo_medio,
)
from esp_datascience.particiones import SEMILLA

SEMILLA_BOOTSTRAP = SEMILLA
N_REPLICAS = 10_000
NIVEL = 0.95
UMBRAL_SUBIDA_NOTABLE_PSI = 1.0
UMBRAL_SUBIDA_GRANDE_PSI = 10.0
UMBRAL_NEGATIVA_GRAVE_PSI = -5.0
UMBRAL_NEGATIVA_MODERADA_PSI = -1.0
# Estos cortes no son leyes de la bomba. Se escribieron en la fase D, después de ver los errores.
# El de 10 psi queda entre el paso mayor observado de M2 y el de M4. Por eso se contrastan otros cortes.
CARACTER_DE_LOS_UMBRALES = "análisis posterior; no es un límite físico ni un protocolo preestablecido"
ESCENARIOS_SUBIDA_AGUA = (
    {"nombre": "publicado", "notable": 1.0, "grande": 10.0},
    {"nombre": "mas_estricto", "notable": 0.5, "grande": 5.0},
    {"nombre": "mas_holgado", "notable": 2.0, "grande": 15.0},
)
ESCENARIOS_NEGATIVAS = (
    {"nombre": "publicado", "grave": -5.0, "moderado": -1.0},
    {"nombre": "mas_estricto", "grave": -2.0, "moderado": -0.5},
    {"nombre": "mas_holgado", "grave": -10.0, "moderado": -5.0},
)
# Lectura fijada por la forma del modelo, no por el MAE observado.
LECTURA_A_PRIORI = {"M1": 3, "M3": 2, "M2": 1, "M4": 0, "M5": 1}
COMPLEJIDAD_INVERTIDA = {"M1": 3, "M3": 2, "M2": 1, "M4": 0, "M5": 1}
CARACTER_DE_LA_PONDERACION = (
    "Propuesta posterior de la fase D. No es la matriz de 2.13 y no cierra la selección."
)
SENTIDO_DE_LAS_PONDERACIONES = {
    "equilibrado": "Cada criterio presente pesa igual.",
    "precision": "Prioriza el puesto por MAE y, en menor grado, la fracción de curvas que mejoran a M1.",
    "tendencia_observada": "Prioriza el agua, el gas y las predicciones negativas de las curvas medidas.",
    "lectura_y_simplicidad": "Prioriza la lectura y la simplicidad de la forma del modelo, sin usar el MAE.",
}
PESOS_SENSIBILIDAD = {
    "equilibrado": {
        "precision": 1, "robustez": 1, "agua": 1, "negativas": 1, "gas": 1, "lectura": 1, "simplicidad": 1,
    },
    "precision": {
        "precision": 4, "robustez": 2, "agua": 1, "negativas": 1, "gas": 1, "lectura": 1, "simplicidad": 1,
    },
    "tendencia_observada": {
        "precision": 1, "robustez": 1, "agua": 4, "negativas": 2, "gas": 3, "lectura": 1, "simplicidad": 1,
    },
    "lectura_y_simplicidad": {
        "precision": 1, "robustez": 1, "agua": 1, "negativas": 1, "gas": 1, "lectura": 4, "simplicidad": 4,
    },
}


def mae_por_curva(predicciones: pd.DataFrame, columna: str) -> pd.Series:
    """Una cifra por curva. Rechaza una curva que tenga un hueco."""
    if predicciones["curva_id"].isna().any():
        raise ValueError("Hay una fila sin curva.")
    incompleta = predicciones.groupby("curva_id")[columna].apply(lambda serie: bool(serie.isna().any()))
    if bool(incompleta.any()):
        raise ValueError(f"{columna} no cubre todas las curvas. Hay que limitar el subconjunto antes.")
    return metrica_por_curva(
        predicciones["medicion"], predicciones[columna], predicciones["curva_id"], error_absoluto_medio
    )


def sesgo_por_curva(predicciones: pd.DataFrame, columna: str) -> pd.Series:
    return metrica_por_curva(
        predicciones["medicion"], predicciones[columna], predicciones["curva_id"], sesgo_medio
    )


def delta_mae(referencia: pd.Series, candidata: pd.Series, exigir_las_mismas: bool = True) -> pd.Series:
    """Candidata menos referencia, una curva cada vez. No rellena ausencias."""
    _exigir_indice_de_curvas(referencia)
    _exigir_indice_de_curvas(candidata)
    if exigir_las_mismas:
        return diferencia_pareada(referencia, candidata)
    comunes = referencia.index.intersection(candidata.index)
    if len(comunes) == 0:
        raise ValueError("No hay curvas en común.")
    return diferencia_pareada(referencia.loc[comunes], candidata.loc[comunes])


def resumen_delta(delta: pd.Series) -> dict:
    _exigir_indice_de_curvas(delta)
    valores = delta.to_numpy(dtype=float)
    return {
        "n_curvas": int(len(valores)),
        "media_psi": float(np.mean(valores)),
        "mediana_psi": float(np.median(valores)),
        "desviacion_psi": float(np.std(valores, ddof=1)) if len(valores) > 1 else float("nan"),
        "minimo_psi": float(np.min(valores)),
        "maximo_psi": float(np.max(valores)),
        "curvas_que_mejoran": int(np.sum(valores < 0)),
        "curvas_que_empeoran": int(np.sum(valores > 0)),
        "curvas_iguales": int(np.sum(valores == 0)),
    }


def bootstrap_media(delta: pd.Series, n_replicas: int = N_REPLICAS, semilla: int = SEMILLA_BOOTSTRAP, nivel: float = NIVEL) -> dict:
    """Intervalo percentil de la media. Remuestrea curvas, no filas."""
    _exigir_indice_de_curvas(delta)
    if n_replicas < 1000:
        raise ValueError("El número de réplicas quedó por debajo del mínimo fijado.")
    if not 0.0 < nivel < 1.0:
        raise ValueError(nivel)
    valores = delta.to_numpy(dtype=float)
    generador = np.random.default_rng(semilla)
    indices = generador.integers(0, len(valores), size=(n_replicas, len(valores)))
    medias = valores[indices].mean(axis=1)
    cola = (1.0 - nivel) / 2.0
    inferior, superior = np.quantile(medias, [cola, 1.0 - cola])
    salida = resumen_delta(delta)
    salida.update(
        {
            "nivel": nivel,
            "n_replicas": int(n_replicas),
            "semilla": int(semilla),
            "intervalo_inferior_psi": float(inferior),
            "intervalo_superior_psi": float(superior),
            "fraccion_de_medias_negativas": float(np.mean(medias < 0)),
            "unidad": "curva",
        }
    )
    return salida


def bootstrap_conglomerados(
    delta: pd.Series,
    conglomerado: pd.Series,
    n_replicas: int = N_REPLICAS,
    semilla: int = SEMILLA_BOOTSTRAP,
    nivel: float = NIVEL,
) -> dict:
    """Remuestrea grupos enteros de curvas. Es una sensibilidad, no otra validación.

    Cada extracción toma conglomerados con reemplazo. Las curvas de un conglomerado
    permanecen juntas. La media es la de las curvas de los conglomerados extraídos:
    un conglomerado repetido cuenta dos veces. Con seis grupos o menos, el intervalo
    es una base limitada y no demuestra generalización.
    """
    _exigir_indice_de_curvas(delta)
    grupos = conglomerado.loc[delta.index]
    if grupos.isna().any():
        raise ValueError("Hay una curva sin conglomerado.")
    if not grupos.index.equals(delta.index):
        raise ValueError("El conglomerado no está alineado con las curvas.")
    etiquetas = grupos.to_numpy()
    unicos = pd.unique(etiquetas)
    if len(unicos) < 2:
        raise ValueError("Hace falta más de un conglomerado.")
    bloques = {etiqueta: delta.loc[grupos.eq(etiqueta)].to_numpy(dtype=float) for etiqueta in unicos}
    generador = np.random.default_rng(semilla)
    medias = np.empty(n_replicas, dtype=float)
    for replica in range(n_replicas):
        elegidos = generador.choice(unicos, size=len(unicos), replace=True)
        muestra = np.concatenate([bloques[etiqueta] for etiqueta in elegidos])
        medias[replica] = float(np.mean(muestra))
    cola = (1.0 - nivel) / 2.0
    inferior, superior = np.quantile(medias, [cola, 1.0 - cola])
    return {
        "n_conglomerados": int(len(unicos)),
        "n_curvas": int(len(delta)),
        "media_psi": float(delta.mean()),
        "intervalo_inferior_psi": float(inferior),
        "intervalo_superior_psi": float(superior),
        "n_replicas": int(n_replicas),
        "semilla": int(semilla),
        "nivel": nivel,
        "unidad": "conglomerado de curvas",
        "base_limitada": bool(len(unicos) <= 6),
    }


def wilcoxon_exploratorio(delta: pd.Series) -> dict:
    """Prueba de rangos con signo sobre las curvas. No es una prueba de mecanismo.

    Las diferencias iguales a cero se excluyen, que es el método `wilcox` de SciPy.
    Doce contrastes de este tipo no tienen una corrección de multiplicidad fijada de antemano.
    """
    _exigir_indice_de_curvas(delta)
    valores = delta.to_numpy(dtype=float)
    ceros = int(np.sum(valores == 0))
    no_nulos = valores[valores != 0]
    if len(no_nulos) < 5:
        return {
            "aplicable": False,
            "n_no_nulos": int(len(no_nulos)),
            "ceros_excluidos": ceros,
            "p": float("nan"),
            "estadistico": float("nan"),
        }
    resultado = wilcoxon(no_nulos, zero_method="wilcox", alternative="two-sided", method="auto")
    return {
        "aplicable": True,
        "n_no_nulos": int(len(no_nulos)),
        "ceros_excluidos": ceros,
        "estadistico": float(resultado.statistic),
        "p": float(resultado.pvalue),
        "supuesto": "La unidad es la curva. Las curvas comparten hoja, velocidad y procedimiento, así que el valor p no es una probabilidad de un experimento independiente.",
    }


def bonferroni_posterior(valores_p: list[float]) -> list[float]:
    """Multiplica cada valor p por el tamaño de la familia y lo corta en 1.

    Es una sensibilidad posterior. No sustituye los valores p originales ni confirma un ganador.
    """
    if len(valores_p) == 0:
        raise ValueError("La familia de comparaciones está vacía.")
    corregidos = []
    for valor in valores_p:
        numero = float(valor)
        if not np.isfinite(numero) or numero < 0:
            raise ValueError("Hay un valor p que no se puede ajustar.")
        corregidos.append(float(min(1.0, numero * len(valores_p))))
    return corregidos


def diagnostico_sin_un_conglomerado(delta: pd.Series, conglomerado: pd.Series) -> pd.DataFrame:
    """Media de ΔMAE al retirar cada conglomerado completo.

    Diagnóstico posterior. No reajusta modelos ni abre una validación externa nueva.
    """
    _exigir_indice_de_curvas(delta)
    grupos = conglomerado.loc[delta.index]
    if grupos.isna().any() or not grupos.index.equals(delta.index):
        raise ValueError("El conglomerado no está alineado con las curvas.")
    media_todas = float(delta.mean())
    filas = []
    for etiqueta in pd.unique(grupos.to_numpy()):
        resto = delta.loc[~grupos.eq(etiqueta)]
        if resto.empty:
            raise ValueError("Retirar el único conglomerado no deja curvas.")
        media = float(resto.mean())
        filas.append(
            {
                "conglomerado_retirado": etiqueta,
                "n_curvas_retiradas": int(grupos.eq(etiqueta).sum()),
                "n_curvas_restantes": int(len(resto)),
                "media_restante_psi": media,
                "mismo_signo": bool(media * media_todas > 0),
                "caracter": "diagnóstico posterior; no es una validación externa nueva",
            }
        )
    return pd.DataFrame(filas)


def meta_de_curvas(predicciones: pd.DataFrame) -> pd.DataFrame:
    return (
        predicciones.groupby("curva_id", sort=True)
        .agg(
            pliegue=("pliegue", "first"),
            hoja=("hoja", "first"),
            velocidad_rpm=("velocidad_rpm", "first"),
            psep_psig=("psep_psig", "first"),
            condicion=("condicion", "first"),
        )
    )


def tabla_por_grupo(mae: pd.Series, meta: pd.DataFrame, columna: str) -> pd.DataFrame:
    marco = meta.loc[mae.index].copy()
    marco["mae"] = mae
    return (
        marco.groupby(columna, sort=True)["mae"]
        .agg(n_curvas="size", mae_medio="mean", mae_maximo="max")
        .reset_index()
    )


def dependencia_de_curvas_extremas(mae: pd.Series) -> dict:
    orden = mae.sort_values(ascending=False)
    return {
        "media_psi": float(mae.mean()),
        "sin_la_peor_psi": float(orden.iloc[1:].mean()),
        "sin_las_tres_peores_psi": float(orden.iloc[3:].mean()) if len(orden) > 3 else float("nan"),
        "curva_peor": str(orden.index[0]),
        "mae_peor_psi": float(orden.iloc[0]),
    }


def resumen_negativas(predicciones: pd.DataFrame, columna: str, modelo: str) -> dict:
    negativas = predicciones.loc[predicciones[columna] < 0]
    return {
        "modelo": modelo,
        "n_predicciones": int(len(negativas)),
        "n_curvas": int(negativas["curva_id"].nunique()) if len(negativas) else 0,
        "minimo_psi": float(predicciones[columna].min()),
        "maximo_psi": float(predicciones[columna].max()),
        "medicion_minima_en_filas_negativas_psi": float(negativas["medicion"].min()) if len(negativas) else float("nan"),
        "medicion_maxima_en_filas_negativas_psi": float(negativas["medicion"].max()) if len(negativas) else float("nan"),
    }


def monotonía_de_agua(predicciones: pd.DataFrame, columnas: dict[str, str]) -> pd.DataFrame:
    """Pasos ascendentes y Spearman en las curvas de agua. No son la misma pregunta."""
    agua = predicciones[predicciones["condicion"].eq("Single Phase")]
    if agua.empty:
        raise ValueError("No hay curvas de agua en esta tabla.")
    filas = []
    for curva, grupo in agua.groupby("curva_id", sort=True):
        orden = np.argsort(grupo["abscisa"].to_numpy(dtype=float), kind="mergesort")
        fila = {"curva_id": curva, "n_puntos": int(len(grupo))}
        medicion = grupo["medicion"].to_numpy(dtype=float)[orden]
        fila["subidas_medicion"] = int(np.sum(np.diff(medicion) > 0))
        for modelo, columna in columnas.items():
            predicha = grupo[columna].to_numpy(dtype=float)[orden]
            if np.isnan(predicha).any():
                fila[f"subidas_{modelo}"] = np.nan
                fila[f"mayor_subida_{modelo}"] = np.nan
                fila[f"spearman_{modelo}"] = np.nan
                continue
            diferencia = np.diff(predicha)
            fila[f"subidas_{modelo}"] = int(np.sum(diferencia > 0))
            fila[f"mayor_subida_{modelo}"] = float(np.max(diferencia)) if len(diferencia) else float("nan")
            fila[f"spearman_{modelo}"] = float(spearmanr(grupo["abscisa"], grupo[columna]).statistic)
        filas.append(fila)
    return pd.DataFrame(filas)


def puntuacion_de_agua(
    monotonia: pd.DataFrame,
    modelo: str,
    umbral_notable: float = UMBRAL_SUBIDA_NOTABLE_PSI,
    umbral_grande: float = UMBRAL_SUBIDA_GRANDE_PSI,
) -> int:
    """Nota discreta. Los umbrales por defecto no son límites físicos."""
    if umbral_grande < umbral_notable:
        raise ValueError("El corte grande tiene que ser al menos el corte notable.")
    subidas = monotonia[f"subidas_{modelo}"].to_numpy(dtype=float)
    mayores = monotonia[f"mayor_subida_{modelo}"].to_numpy(dtype=float)
    if np.isnan(subidas).any():
        return 0
    if int(np.sum(subidas)) == 0:
        return 3
    if float(np.nanmax(mayores)) >= umbral_grande:
        return 0
    if float(np.nanmax(mayores)) >= umbral_notable:
        return 1
    return 2


def puntuacion_de_negativas(
    resumen: dict,
    umbral_grave: float = UMBRAL_NEGATIVA_GRAVE_PSI,
    umbral_moderado: float = UMBRAL_NEGATIVA_MODERADA_PSI,
) -> int:
    """Nota discreta del mínimo. Cero predicciones negativas sigue valiendo 3."""
    if umbral_grave > umbral_moderado or umbral_moderado >= 0:
        raise ValueError("Los cortes de una predicción negativa tienen que ser negativos y estar ordenados.")
    if resumen["n_predicciones"] == 0:
        return 3
    minimo = resumen["minimo_psi"]
    if minimo <= umbral_grave:
        return 0
    if minimo <= umbral_moderado:
        return 1
    return 2


def notas_de_agua_bajo_umbrales(monotonia: pd.DataFrame, escenarios=ESCENARIOS_SUBIDA_AGUA) -> pd.DataFrame:
    """Repite la nota de agua con cortes redondos. No elige el corte que favorece a un modelo."""
    modelos = [
        columna.removeprefix("subidas_")
        for columna in monotonia.columns
        if columna.startswith("subidas_") and columna != "subidas_medicion"
    ]
    filas = []
    for escenario in escenarios:
        for modelo in modelos:
            filas.append(
                {
                    "escenario": escenario["nombre"],
                    "notable_psi": escenario["notable"],
                    "grande_psi": escenario["grande"],
                    "modelo": modelo,
                    "nota": puntuacion_de_agua(
                        monotonia, modelo, escenario["notable"], escenario["grande"]
                    ),
                    "caracter": CARACTER_DE_LOS_UMBRALES,
                }
            )
    return pd.DataFrame(filas)


def notas_de_negativas_bajo_umbrales(resumenes: list[dict], escenarios=ESCENARIOS_NEGATIVAS) -> pd.DataFrame:
    filas = []
    for escenario in escenarios:
        for resumen in resumenes:
            filas.append(
                {
                    "escenario": escenario["nombre"],
                    "grave_psi": escenario["grave"],
                    "moderado_psi": escenario["moderado"],
                    "modelo": resumen["modelo"],
                    "nota": puntuacion_de_negativas(resumen, escenario["grave"], escenario["moderado"]),
                    "caracter": CARACTER_DE_LOS_UMBRALES,
                }
            )
    return pd.DataFrame(filas)


def pesos_efectivos(pesos: dict[str, float], columnas) -> dict:
    """Muestra qué criterios se omiten y cómo queda el resto al reescalar.

    Surging no tiene curvas de agua. Omitir ese criterio cambia la suma de los otros.
    """
    if any(valor < 0 for valor in pesos.values()):
        raise ValueError("Un peso negativo invertiría el criterio.")
    presentes = {criterio: peso for criterio, peso in pesos.items() if criterio in columnas and peso > 0}
    if not presentes:
        raise ValueError("Ningún peso coincide con las columnas.")
    total = float(sum(presentes.values()))
    omitidos = [criterio for criterio in pesos if criterio not in presentes]
    return {
        "pesos_renormalizados": {criterio: peso / total for criterio, peso in presentes.items()},
        "omitidos": omitidos,
        "renormaliza": bool(omitidos),
    }


def detalle_de_ponderacion(puntuaciones: pd.DataFrame) -> pd.DataFrame:
    """Puestos completos de cada escenario. No declara un ganador."""
    filas = []
    for nombre, pesos in PESOS_SENSIBILIDAD.items():
        info = pesos_efectivos(pesos, puntuaciones.columns)
        orden = ranking_con_pesos(puntuaciones, pesos)
        for puesto, (modelo, nota) in enumerate(orden.items(), start=1):
            filas.append(
                {
                    "ponderacion": nombre,
                    "modelo": modelo,
                    "puesto": puesto,
                    "puntuacion": float(nota),
                    "criterios_omitidos": ",".join(info["omitidos"]),
                    "caracter": CARACTER_DE_LA_PONDERACION,
                }
            )
    return pd.DataFrame(filas)


def ranking_con_pesos(puntuaciones: pd.DataFrame, pesos: dict[str, float]) -> pd.Series:
    """Suma ponderada. Una puntuación alta es más favorable en ese criterio.

    Si un criterio no está en la tabla, se omite y el resto se reescala.
    Así surging no recibe una nota de curvas de agua que no tiene.
    """
    if any(valor < 0 for valor in pesos.values()):
        raise ValueError("Un peso negativo invertiría el criterio.")
    presentes = {criterio: peso for criterio, peso in pesos.items() if criterio in puntuaciones.columns and peso > 0}
    if not presentes:
        raise ValueError("Ningún peso coincide con las columnas.")
    total = sum(presentes.values())
    acumulado = sum(puntuaciones[criterio] * (peso / total) for criterio, peso in presentes.items())
    return acumulado.sort_values(ascending=False)


def primeros_por_ponderacion(puntuaciones: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for nombre, pesos in PESOS_SENSIBILIDAD.items():
        orden = ranking_con_pesos(puntuaciones, pesos)
        filas.append(
            {
                "ponderacion": nombre,
                "primero": orden.index[0],
                "segundo": orden.index[1],
                "puntuacion_primero": float(orden.iloc[0]),
            }
        )
    return pd.DataFrame(filas)


def puntuacion_por_subidas_de_gas(n_grupos_que_suben: int, modo: str = "escalonado") -> int:
    if n_grupos_que_suben < 0:
        raise ValueError(n_grupos_que_suben)
    if modo == "binario":
        return 3 if n_grupos_que_suben == 0 else 0
    if modo != "escalonado":
        raise ValueError(modo)
    if n_grupos_que_suben == 0:
        return 3
    if n_grupos_que_suben == 1:
        return 2
    if n_grupos_que_suben <= 3:
        return 1
    return 0


def puntuacion_por_spearman(peor_spearman: float, cortes: tuple[float, float, float] = (-0.999, -0.95, -0.90)) -> int:
    """`peor_spearman` es el valor menos negativo: el que más se aleja de una caída estricta."""
    if not (cortes[0] < cortes[1] < cortes[2] < 0):
        raise ValueError("Los cortes de Spearman tienen que ir de más estricto a menos estricto.")
    if peor_spearman <= cortes[0]:
        return 3
    if peor_spearman <= cortes[1]:
        return 2
    if peor_spearman <= cortes[2]:
        return 1
    return 0


def subidas_en_caudal_comun(predicciones: pd.DataFrame, columnas: dict[str, str]) -> pd.DataFrame:
    """Interpola en el centro del caudal común. No extrapola y no reentrena."""
    gas = predicciones[predicciones["condicion"].ne("Single Phase")].copy()
    if gas.empty or not gas["condicion"].astype(str).str.startswith("Qgd=").all():
        raise ValueError("Esta descripción es solo de las curvas con Qgd.")
    gas["qgd"] = gas["condicion"].str.replace("Qgd=", "", regex=False).astype(float)
    nombres = ["medicion", *columnas]
    serie_de = {"medicion": "medicion", **columnas}
    filas = []
    for (hoja, velocidad), bloque in gas.groupby(["hoja", "velocidad_rpm"], sort=True):
        partes = [grupo for _, grupo in bloque.groupby("condicion", sort=True)]
        inferior = max(float(grupo["abscisa"].min()) for grupo in partes)
        superior = min(float(grupo["abscisa"].max()) for grupo in partes)
        if superior <= inferior:
            continue
        caudal = 0.5 * (inferior + superior)
        valores = {nombre: [] for nombre in nombres}
        for grupo in sorted(partes, key=lambda item: float(item["qgd"].iloc[0])):
            agregado = grupo.groupby("abscisa", as_index=False)[list(serie_de.values())].mean().sort_values("abscisa")
            xs = agregado["abscisa"].to_numpy(dtype=float)
            if caudal < xs[0] or caudal > xs[-1]:
                continue
            for nombre, columna in serie_de.items():
                valores[nombre].append(float(np.interp(caudal, xs, agregado[columna].to_numpy(dtype=float))))
        for nombre in nombres:
            diferencia = np.diff(valores[nombre])
            filas.append(
                {
                    "hoja": hoja,
                    "velocidad_rpm": int(velocidad),
                    "serie": nombre,
                    "n_pasos": int(len(diferencia)),
                    "pasos_que_suben": int(np.sum(diferencia > 0)),
                    "es_prediccion_original": False,
                }
            )
    return pd.DataFrame(filas)


def origen_de_velocidad(tabla_mapping: pd.DataFrame) -> pd.DataFrame:
    """Una procedencia por hoja. Si una hoja mezclara las dos, el contraste no serviría."""
    filas = []
    for hoja, grupo in tabla_mapping.groupby("hoja", sort=True):
        origenes = sorted(grupo["origen_velocidad"].dropna().unique())
        if len(origenes) != 1:
            raise ValueError(f"La hoja {hoja} mezcla procedencias de velocidad.")
        filas.append(
            {
                "hoja": hoja,
                "origen_velocidad": origenes[0],
                "psep_psig": float(grupo["psep_psig"].iloc[0]),
                "n_filas": int(len(grupo)),
                "n_curvas": int(grupo.groupby(["velocidad_rpm", "condicion"]).ngroups),
            }
        )
    return pd.DataFrame(filas)


def _exigir_indice_de_curvas(serie: pd.Series) -> None:
    if not isinstance(serie, pd.Series) or serie.empty:
        raise ValueError("Hace falta una serie con una curva por fila.")
    if serie.index.has_duplicates:
        raise ValueError("El remuestreo exige una sola diferencia por curva.")
    if serie.isna().any() or not np.isfinite(serie.to_numpy(dtype=float)).all():
        raise ValueError("Hay una curva sin diferencia finita.")
