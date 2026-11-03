"""Comprobaciones de conteo de la actividad 2.12.

`pares_por_hoja` es la función del cuaderno. `comprobar_conteos_publicados`
reúne las mismas comprobaciones que esa celda ejecuta sobre las dos tablas.
"""

import pandas as pd


def pares_por_hoja(tabla: pd.DataFrame) -> dict[str, int]:
    return tabla.groupby("hoja", observed=True).size().to_dict()


def comprobar_conteos_publicados(mapping_largo: pd.DataFrame, surging_largo: pd.DataFrame) -> None:
    auditoria_mapping = {"50psig": 186, "100psig": 192, "150psig": 192}
    auditoria_surging = {"50psig": 119, "100psig": 129, "150psig": 139}
    obtenido_mapping = pares_por_hoja(mapping_largo)
    obtenido_surging = pares_por_hoja(surging_largo)
    for hoja, esperado in auditoria_mapping.items():
        obtenido = int(obtenido_mapping[hoja])
        if obtenido != esperado:
            raise AssertionError(f"mapping/{hoja} no reproduce la auditoría.")
    for hoja, esperado in auditoria_surging.items():
        obtenido = int(obtenido_surging[hoja])
        if obtenido != esperado:
            raise AssertionError(f"surging/{hoja} no reproduce la auditoría.")

    solo_50 = mapping_largo[mapping_largo["hoja"] == "50psig"]
    condiciones_50 = solo_50.groupby(["velocidad_rpm", "condicion"], observed=True).ngroups
    pares_1800 = int((solo_50["velocidad_rpm"] == 1800).sum())
    pares_3500 = int((solo_50["velocidad_rpm"] == 3500).sum())
    if (len(solo_50), condiciones_50, pares_1800, pares_3500) != (186, 10, 62, 124):
        raise AssertionError("Mapping/50psig no reproduce 186 / 10 / 62 / 124.")

    if set(mapping_largo.loc[mapping_largo["hoja"] == "50psig", "origen_velocidad"]) != {"celda"}:
        raise AssertionError("La velocidad de Mapping/50psig tenía que salir de la celda.")
    diseno = mapping_largo[mapping_largo["hoja"].isin(["100psig", "150psig"])]
    if set(diseno["origen_velocidad"]) != {"diseño_experimental"}:
        raise AssertionError("La velocidad de 100 y 150 psig tenía que quedar marcada como diseño.")
    if diseno["valor_celda_velocidad"].notna().any():
        raise AssertionError("Una hoja sin velocidad escrita quedó con un número de celda.")
    if set(surging_largo["origen_velocidad"]) != {"celda"}:
        raise AssertionError("La velocidad de surging tenía que salir de la celda.")
    if mapping_largo["ql_bpd"].isna().any() or mapping_largo["dp2_3_psi"].isna().any():
        raise AssertionError("Entró una medición vacía a la tabla de mapping.")
    if surging_largo["gvf0_porcentaje"].isna().any() or surging_largo["dp2_3_psi"].isna().any():
        raise AssertionError("Entró una medición vacía a la tabla de surging.")
    if (surging_largo["gvf0_porcentaje"] > 1).sum() == 0:
        raise AssertionError("GVF0 no supera 1. La lectura en porcentaje quedaría sin apoyo en estos números.")
