"""Curva de bomba a la velocidad actual e intersección con la THD total.

Transcribe el bloque «Curva de Performance de Bomba» (velocidad actual) y el
bloque «Descarga» de cada hoja, que producen «Caudal a producir».

Fórmulas de la hoja (QF-554H, filas 86-91 y 94-97):
    Q_i  = Q60_i * (f / f_curva)
    H_i  = H60_i * (f / f_curva)^2 * etapas
    k    = MATCH(THD, H, -1)        (H en orden descendente: último H >= THD)
    Q    = Q_k + (THD - H_k) / (H_k+1 - H_k) * (Q_k+1 - Q_k)

Las exponentes 1 y 2 son las leyes de afinidad que la propia hoja usa. Este
módulo no valida que sean adecuadas para esta bomba; las transcribe.
"""

from __future__ import annotations

from modelo_deterministico.resultado import Resultado


def curva_a_velocidad(
    curva_60: list[dict],
    frecuencia_hz: float,
    frecuencia_curva_hz: float,
    etapas: float,
) -> list[dict]:
    """Escala la tabla de la bomba a la velocidad actual, como las filas 86-91."""
    razon = frecuencia_hz / frecuencia_curva_hz
    return [
        {
            "caudal_bfpd": p["caudal_bfpd"] * razon,
            "head_ft": p["head_ft"] * (razon**2) * etapas,
        }
        for p in curva_60
    ]


def _match_descendente(valor: float, cabezas: list[float]) -> int | None:
    """Réplica de MATCH(valor, rango, -1): posición (base 0) del menor valor >= buscado.

    Excel exige el rango en orden descendente y devuelve #N/A si el buscado es
    mayor que el primero. Aquí se devuelve None en ese caso.
    """
    posicion = None
    for i, h in enumerate(cabezas):
        if h >= valor:
            posicion = i
        else:
            break
    return posicion


def caudal_a_producir(
    thd_total_ft: float | None,
    curva_60: list[dict],
    frecuencia_hz: float | None,
    frecuencia_curva_hz: float | None,
    etapas: float | None,
) -> Resultado:
    """Caudal donde la altura de la bomba a la velocidad actual iguala la THD total."""
    entradas = {
        "thd_total_ft": {"valor": thd_total_ft, "unidad": "ft"},
        "frecuencia_hz": {"valor": frecuencia_hz, "unidad": "Hz"},
        "frecuencia_curva_hz": {"valor": frecuencia_curva_hz, "unidad": "Hz"},
        "etapas": {"valor": etapas, "unidad": "n"},
        "puntos_de_curva": {"valor": len(curva_60), "unidad": "n"},
    }
    ecuaciones = ["BES-jun curva a velocidad", "BES-jun MATCH/INDEX de Descarga"]
    faltan = [
        k
        for k, v in entradas.items()
        if v["valor"] is None or (k == "puntos_de_curva" and v["valor"] < 2)
    ]
    if faltan:
        return Resultado(
            estado="no_calculable",
            motivo="Faltan entradas esenciales de la intersección: " + ", ".join(faltan),
            entradas=entradas,
            ecuaciones=ecuaciones,
            alertas=["dato_faltante"],
        )
    if frecuencia_curva_hz <= 0 or frecuencia_hz <= 0 or etapas <= 0:
        return Resultado(
            estado="no_calculable",
            motivo="Frecuencia o etapas no positivas.",
            entradas=entradas,
            ecuaciones=ecuaciones,
            alertas=["fuera_de_dominio"],
        )
    puntos = curva_a_velocidad(curva_60, frecuencia_hz, frecuencia_curva_hz, etapas)
    cabezas = [p["head_ft"] for p in puntos]
    if any(cabezas[i] < cabezas[i + 1] for i in range(len(cabezas) - 1)):
        return Resultado(
            estado="no_calculable",
            motivo="La curva de head no es descendente; MATCH(-1) de la hoja no aplica.",
            entradas=entradas,
            ecuaciones=ecuaciones,
            alertas=["fuera_de_dominio"],
        )
    k = _match_descendente(thd_total_ft, cabezas)
    if k is None:
        return Resultado(
            estado="no_calculable",
            motivo=(
                "La THD total supera el head de la bomba a la velocidad actual en todos los "
                "puntos de la curva. La hoja devolvería #N/A."
            ),
            entradas=entradas,
            ecuaciones=ecuaciones,
            alertas=["fuera_de_curva_superior"],
        )
    if k + 1 >= len(puntos):
        return Resultado(
            estado="no_calculable",
            motivo=(
                "La THD total queda por debajo del último punto de la curva. "
                "La hoja no tiene punto siguiente para interpolar (#REF!)."
            ),
            entradas=entradas,
            ecuaciones=ecuaciones,
            alertas=["fuera_de_curva_inferior"],
        )
    x0, x1 = cabezas[k], cabezas[k + 1]
    q0, q1 = puntos[k]["caudal_bfpd"], puntos[k + 1]["caudal_bfpd"]
    caudal = q0 + ((thd_total_ft - x0) / (x1 - x0)) * (q1 - q0)
    return Resultado(
        estado="calculable",
        motivo="Intersección transcrita de la hoja: interpolación lineal en la curva a la velocidad actual.",
        entradas=entradas,
        resultados={
            "caudal_a_producir_bfpd": {
                "valor": caudal,
                "unidad": "BFPD",
                "formula": "BES-jun Caudal a producir",
            },
            "posicion_tramo": {"valor": k + 1, "unidad": "índice base 1 del MATCH"},
        },
        ecuaciones=ecuaciones,
        advertencias=[
            "Interpolación lineal entre dos puntos de una tabla de seis; no es una curva ajustada.",
            "Las leyes de afinidad (exponentes 1 y 2) son las de la hoja; no se verificaron para esta bomba.",
            "Reproduce la hoja. La comparación con el caudal medido es un contraste, no una validación independiente.",
        ],
    )
