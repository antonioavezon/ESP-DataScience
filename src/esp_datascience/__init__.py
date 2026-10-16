"""Copia reutilizable de las funciones del cuaderno de normalización.

Los cuadernos siguen teniendo su propio código. Estos módulos no sustituyen
esa lectura. Sirven para pruebas y para un uso posterior fuera del cuaderno.
"""

from esp_datascience.lectura import es_numero, filas_de_franja_mapping, psep_de_hoja
from esp_datascience.normalizacion import (
    FRACCION_QBEP,
    filas_de_franja_surging,
    normalizar_mapping,
    normalizar_surging,
    velocidad_segun_diseno,
)
from esp_datascience.rutas import encontrar_raiz_laboratorio, huella_sha256
from esp_datascience.validacion import comprobar_conteos_publicados, pares_por_hoja

__all__ = [
    "FRACCION_QBEP",
    "comprobar_conteos_publicados",
    "encontrar_raiz_laboratorio",
    "es_numero",
    "filas_de_franja_mapping",
    "filas_de_franja_surging",
    "huella_sha256",
    "normalizar_mapping",
    "normalizar_surging",
    "pares_por_hoja",
    "psep_de_hoja",
    "velocidad_segun_diseno",
]
