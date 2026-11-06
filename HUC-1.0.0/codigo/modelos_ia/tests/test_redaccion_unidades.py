"""Regresión: la redacción del modelo no puede alterar la unidad de una magnitud.

Observado con qwen3:4b-instruct en la comparación QF-084/QF-301:
«10535.17 BFP-DF» en lugar de «10535.17 BFPD». La cifra existía en los hechos,
por eso la guarda de cifras lo aceptaba.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from modelos_ia.redaccion import elegir  # noqa: E402

CORPUS = (
    "QF-301: admisión 1558.04 ft, caudal de intersección 8280.86 BFPD. "
    "QF-084: admisión 1714.5 ft, caudal de intersección 10535.17 BFPD. "
    "Gradiente 0.43 psi/ft. Frecuencia 63 Hz."
)
RESPALDO = "QF-084: caudal de intersección 10535.17 BFPD."
POZOS = ["QF-084", "QF-301"]


def test_rechaza_unidad_corrompida():
    propuesto = "El caudal de QF-301 es 8280.86 BFPD, mientras que el de QF-084 es 10535.17 BFP-DF."
    assert elegir(RESPALDO, propuesto, CORPUS, [], POZOS) == RESPALDO


def test_rechaza_unidad_ajena_a_los_hechos():
    propuesto = "El caudal de QF-084 es 10535.17 m3/d."
    assert elegir(RESPALDO, propuesto, CORPUS, [], POZOS) == RESPALDO


def test_acepta_unidades_presentes_en_los_hechos():
    propuesto = "QF-084 entrega 10535.17 BFPD con 63 Hz y un gradiente de 0.43 psi/ft; su admisión es 1714.5 ft."
    assert elegir(RESPALDO, propuesto, CORPUS, [], POZOS) == propuesto


def test_palabras_en_minuscula_tras_cifra_no_bloquean():
    propuesto = "Se comparan 2 pozos: QF-084 tiene 1714.5 ft de admisión y QF-301 1558.04 ft."
    corpus = CORPUS + " 2"
    assert elegir(RESPALDO, propuesto, corpus, [], POZOS) == propuesto
