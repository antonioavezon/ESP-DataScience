"""Transformación de las hojas anchas a tablas largas.

El texto de estas funciones es el de `notebooks/02_normalizacion.ipynb`.
"""

import pandas as pd

from esp_datascience.lectura import es_numero, filas_de_franja_mapping, psep_de_hoja

CONJUNTO_1800 = frozenset({"Qgd=0.005", "Qgd=0.01", "Qgd=0.015"})
CONJUNTO_3500 = frozenset({"Qgd=0.01", "Qgd=0.02", "Qgd=0.03", "Qgd=0.04", "Qgd=0.05"})
FRACCION_QBEP = {"0.75Qbep": 0.75, "Qbep": 1.0, "1.25Qbep": 1.25}


def velocidad_segun_diseno(rotulos_qgd: set[str]) -> int:
    conjunto = frozenset(rotulos_qgd)
    if conjunto == CONJUNTO_1800:
        return 1800
    if conjunto == CONJUNTO_3500:
        return 3500
    raise ValueError("El conjunto de Qgd no está en el diseño experimental: " + ", ".join(sorted(conjunto)))


def columnas_separadoras_vacias(tabla: pd.DataFrame) -> None:
    for columna in (3, 6, 9, 12, 15):
        if tabla[columna].notna().any():
            raise AssertionError(f"La columna separadora {columna} de mapping ya no está vacía.")


def normalizar_mapping(tabla: pd.DataFrame, hoja: str) -> tuple[pd.DataFrame, int]:
    columnas_separadoras_vacias(tabla)
    filas_franja = filas_de_franja_mapping(tabla)
    if len(filas_franja) != 2:
        raise ValueError(f"{hoja}: se esperaban dos franjas de mapping.")
    registros = []
    huecos = 0
    for indice, fila_condicion in enumerate(filas_franja):
        fila_encabezado = fila_condicion + 1
        fila_fin = filas_franja[indice + 1] if indice + 1 < len(filas_franja) else len(tabla)
        condiciones = []
        for columna in range(tabla.shape[1]):
            rotulo = tabla.iat[fila_condicion, columna]
            if isinstance(rotulo, str):
                condiciones.append((columna, rotulo))
        rotulos_qgd = [rotulo for _, rotulo in condiciones if rotulo.startswith("Qgd=")]
        velocidad_diseno = velocidad_segun_diseno(set(rotulos_qgd))
        fila_celda = fila_encabezado + 1
        celda = tabla.iat[fila_celda, 0]
        if es_numero(celda):
            if int(celda) != velocidad_diseno:
                raise ValueError(
                    f"{hoja}: la celda de velocidad no coincide con el diseño experimental."
                )
            origen = "celda"
            valor_celda = int(celda)
        elif pd.isna(celda):
            origen = "diseño_experimental"
            valor_celda = pd.NA
        else:
            raise ValueError(f"{hoja}: la celda de velocidad no es un número ni está vacía.")
        for columna, condicion in condiciones:
            if tabla.iat[fila_encabezado, columna] != "Flow rate":
                raise ValueError(f"{hoja}: falta el rótulo Flow rate.")
            if tabla.iat[fila_encabezado, columna + 1] != "DP2-3":
                raise ValueError(f"{hoja}: falta el rótulo DP2-3.")
            qgd = pd.NA if condicion == "Single Phase" else float(condicion.split("=", 1)[1])
            for fila in range(fila_celda, fila_fin):
                caudal = tabla.iat[fila, columna]
                incremento = tabla.iat[fila, columna + 1]
                hay_caudal = es_numero(caudal)
                hay_incremento = es_numero(incremento)
                if not hay_caudal and not hay_incremento:
                    huecos += 1
                    continue
                if hay_caudal != hay_incremento:
                    raise ValueError(
                        f"{hoja}, fila {fila}: el par está incompleto y no se imputa."
                    )
                registros.append(
                    {
                        "archivo": "mapping.xlsx",
                        "hoja": hoja,
                        "psep_psig": psep_de_hoja(hoja),
                        "psep_unidad": "psig",
                        "certeza_psep": "Alta",
                        "fila": fila,
                        "columna_condicion": columna,
                        "columna_caudal": columna,
                        "columna_dp": columna + 1,
                        "condicion": condicion,
                        "qgd": qgd,
                        "velocidad_rpm": velocidad_diseno,
                        "velocidad_unidad": "rpm",
                        "origen_velocidad": origen,
                        "fila_celda_velocidad": fila_celda,
                        "columna_celda_velocidad": 0,
                        "valor_celda_velocidad": valor_celda,
                        "certeza_velocidad": "Alta",
                        "ql_bpd": float(caudal),
                        "ql_unidad": "bpd",
                        "certeza_ql": "Alta, como interpretación",
                        "dp2_3_psi": float(incremento),
                        "dp2_3_unidad": "psi",
                        "certeza_dp": "Media",
                    }
                )
    return pd.DataFrame(registros), huecos


def filas_de_franja_surging(tabla: pd.DataFrame) -> list[int]:
    filas = []
    for fila in range(len(tabla)):
        for columna in range(tabla.shape[1]):
            valor = tabla.iat[fila, columna]
            if isinstance(valor, str) and valor in FRACCION_QBEP:
                filas.append(fila)
                break
    return filas


def normalizar_surging(tabla: pd.DataFrame, hoja: str) -> tuple[pd.DataFrame, int]:
    filas_franja = filas_de_franja_surging(tabla)
    if len(filas_franja) != 2:
        raise ValueError(f"{hoja}: se esperaban dos franjas de surging.")
    registros = []
    huecos = 0
    for indice, fila_condicion in enumerate(filas_franja):
        fila_rotulos = fila_condicion + 1
        fila_fin = filas_franja[indice + 1] if indice + 1 < len(filas_franja) else len(tabla)
        condiciones = []
        for columna in range(tabla.shape[1]):
            rotulo = tabla.iat[fila_condicion, columna]
            if isinstance(rotulo, str):
                if rotulo == "Rotary Speed (rpm)":
                    continue
                if rotulo not in FRACCION_QBEP:
                    raise ValueError(f"{hoja}: condición de surging no reconocida.")
                condiciones.append((columna, rotulo))
        if [columna for columna, _ in condiciones] != [1, 4, 7]:
            raise ValueError(f"{hoja}: las condiciones de surging no están en las columnas 1, 4 y 7.")
        velocidades = []
        for columna, _ in condiciones:
            celda = tabla.iat[fila_rotulos, columna - 1]
            if not es_numero(celda):
                raise ValueError(f"{hoja}: falta la velocidad escrita de surging. No se imputa.")
            velocidades.append(int(celda))
        if len(set(velocidades)) != 1:
            raise ValueError(f"{hoja}: las tres celdas de velocidad de la franja no coinciden.")
        velocidad = velocidades[0]
        if velocidad not in (1800, 3500):
            raise ValueError(f"{hoja}: la velocidad escrita no es 1800 ni 3500 rpm.")
        for columna, condicion in condiciones:
            if tabla.iat[fila_rotulos, columna] != "GVF0":
                raise ValueError(f"{hoja}: falta el rótulo GVF0.")
            if tabla.iat[fila_rotulos, columna + 1] != "DP2-3":
                raise ValueError(f"{hoja}: falta el rótulo DP2-3.")
            for fila in range(fila_rotulos + 1, fila_fin):
                gvf = tabla.iat[fila, columna]
                incremento = tabla.iat[fila, columna + 1]
                hay_gvf = es_numero(gvf)
                hay_incremento = es_numero(incremento)
                if not hay_gvf and not hay_incremento:
                    huecos += 1
                    continue
                if hay_gvf != hay_incremento:
                    raise ValueError(
                        f"{hoja}, fila {fila}: el par de surging está incompleto y no se imputa."
                    )
                registros.append(
                    {
                        "archivo": "surging.xlsx",
                        "hoja": hoja,
                        "psep_psig": psep_de_hoja(hoja),
                        "psep_unidad": "psig",
                        "certeza_psep": "Alta",
                        "fila": fila,
                        "columna_condicion": columna,
                        "columna_gvf": columna,
                        "columna_dp": columna + 1,
                        "condicion": condicion,
                        "fraccion_qbep": FRACCION_QBEP[condicion],
                        "velocidad_rpm": velocidad,
                        "velocidad_unidad": "rpm",
                        "origen_velocidad": "celda",
                        "fila_celda_velocidad": fila_rotulos,
                        "columna_celda_velocidad": columna - 1,
                        "valor_celda_velocidad": velocidad,
                        "certeza_velocidad": "Alta",
                        "gvf0_porcentaje": float(gvf),
                        "gvf0_unidad": "porcentaje",
                        "certeza_gvf": "Media",
                        "dp2_3_psi": float(incremento),
                        "dp2_3_unidad": "psi",
                        "certeza_dp": "Media",
                    }
                )
    return pd.DataFrame(registros), huecos
