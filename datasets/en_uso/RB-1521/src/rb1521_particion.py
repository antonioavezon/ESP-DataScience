"""Partición de caudal que el libro cumple cuando el caudal del día es el de la prueba.

Q-water = Q-fluidos × BSW
Q-oil = Q-fluidos − Q-water

No es una fórmula de bomba. Cierra en 128 de las 129 filas.
La excepción almacenada es el 2020-07-09: ese día el producto no reproduce Q-water ni Q-oil.
"""

from __future__ import annotations


def particionar(caudal_fluidos: float, bsw: float) -> tuple[float, float]:
    agua = caudal_fluidos * bsw
    petroleo = caudal_fluidos - agua
    return agua, petroleo


def identidad_exacta(fila: dict, tolerancia: float = 1e-9) -> bool:
    """True solo si las tres columnas numéricas cierran la partición."""
    caudal = fila.get("Q-fluidos")
    agua = fila.get("Q-water")
    petroleo = fila.get("Q-oil")
    bsw = fila.get("BSW")
    if not all(isinstance(valor, (int, float)) and not isinstance(valor, bool) for valor in (caudal, agua, petroleo, bsw)):
        return False
    calculada_agua, calculado_petroleo = particionar(float(caudal), float(bsw))
    return abs(calculada_agua - float(agua)) <= tolerancia and abs(calculado_petroleo - float(petroleo)) <= tolerancia


def contar_identidades(serie: list[dict]) -> int:
    return sum(1 for fila in serie if identidad_exacta(fila))
