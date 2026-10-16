"""Síntesis de la fase E.

No reajusta M1M5, no cambia el protocolo 2.14-A y no elige un ganador con pesos nuevos.
El menor MAE se lee de la tabla que ya existe. M1 y M2 conservan el papel que tenían
antes de ver el error externo: piso interpretable y polinomio declarado.
"""

from __future__ import annotations

REFERENCIA_INTERPRETABLE = "M1"
REFERENCIA_NO_LINEAL = "M2"
REFERENCIA_SEMIEMPIRICA = "M5"
MODELOS_GLOBALES = ("M1", "M2", "M3", "M4")


def papeles(maes_por_protocolo: dict[str, dict[str, float]]) -> dict:
    """Clasifica papeles de referencia. No calcula una nota ponderada.

    `maes_por_protocolo` trae el MAE medio por curva, en psi, de M1 a M4.
    M5 no entra: su cobertura no es la del protocolo completo.
    """
    if not maes_por_protocolo:
        raise ValueError("Hace falta al menos un protocolo.")
    mejor = {}
    for protocolo, cifras in maes_por_protocolo.items():
        if set(cifras) != set(MODELOS_GLOBALES):
            raise ValueError(f"{protocolo} debe traer exactamente M1, M2, M3 y M4.")
        if any(valor != valor or valor < 0 for valor in cifras.values()):
            raise ValueError("El MAE tiene que ser finito y no negativo.")
        orden = sorted(cifras, key=lambda modelo: (float(cifras[modelo]), modelo))
        mejor[protocolo] = orden[0]
    precisos = set(mejor.values())
    return {
        "mejor_precision_por_protocolo": mejor,
        "candidato_de_precision": next(iter(precisos)) if len(precisos) == 1 else None,
        "referencia_interpretable": REFERENCIA_INTERPRETABLE,
        "referencia_no_lineal": REFERENCIA_NO_LINEAL,
        "referencia_semiempirica": REFERENCIA_SEMIEMPIRICA,
        "ganador_unico": None,
        "motivo": (
            "No hay un ganador único. El menor MAE no cumple por sí solo la regla de superioridad de 2.13."
        ),
    }


def resumen_de_m5(mae_por_modelo: dict[str, float], n_curvas: int, n_curvas_del_protocolo: int) -> dict:
    """M5 solo se lee en las curvas donde la referencia de agua está completa.

    `mae_por_modelo` es el MAE medio por curva, en psi, calculado en ese subconjunto.
    No se acepta usar las curvas de todo el protocolo como si M5 las cubriera.
    """
    cifras = {str(modelo): float(valor) for modelo, valor in mae_por_modelo.items()}
    if "M5" not in cifras:
        raise ValueError("El subconjunto tiene que incluir a M5.")
    if int(n_curvas) <= 0 or int(n_curvas) >= int(n_curvas_del_protocolo):
        raise ValueError("M5 no se compara con todas las curvas del protocolo.")
    return {
        "n_curvas": int(n_curvas),
        "n_curvas_del_protocolo": int(n_curvas_del_protocolo),
        "cobertura_parcial": True,
        "mae_m5_psi": float(cifras["M5"]),
        "mae_en_el_mismo_subconjunto_psi": cifras,
    }
