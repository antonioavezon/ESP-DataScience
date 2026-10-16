"""Funciones reutilizables del laboratorio.

Los cuadernos siguen mostrando su propio código. Estos módulos no sustituyen
esa lectura. La normalización reproduce la actividad 2.12. Las particiones
de la actividad 2.14 no entrenan modelos.
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
from esp_datascience.metricas import error_absoluto_medio
from esp_datascience.particiones import SEMILLA, auditar_particiones, marcar_pliegues
from esp_datascience.protocolo import VERSION
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
    "SEMILLA",
    "error_absoluto_medio",
    "VERSION",
    "auditar_particiones",
    "marcar_pliegues",
    "pares_por_hoja",
    "psep_de_hoja",
    "velocidad_segun_diseno",
]
