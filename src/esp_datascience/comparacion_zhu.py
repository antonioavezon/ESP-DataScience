"""Comparación documental de la actividad 2.15.

No reentrena los modelos de la actividad 2.14 y no implementa una
correlación de Zhu. Solo registra cuándo una comparación numérica
estaría justificada.
"""

from __future__ import annotations

PARES_NO_EQUIVALENTES = (
    (
        "qgd",
        "gvf0_porcentaje",
        "En la tesis, Qgd es Qg/Qmax y GVF es Qg/(Qg+Ql). No son el mismo número.",
    ),
    (
        "dp2_3_psi",
        "presion_absoluta",
        "dp2_3_psi es un incremento de presión de etapa, no una presión absoluta ni de fondo.",
    ),
    (
        "dp2_3_psi",
        "frontera_de_patron",
        "El artículo de 2019 predice fronteras de patrón de flujo, no el incremento punto a punto.",
    ),
)

CONDICIONES_NUMERICAS = (
    "objetivo_comun",
    "unidades_comunes",
    "protocolo_comun",
    "ecuacion_verificada",
    "datos_disponibles",
    "dominio_conocido",
)


def exigir_comparacion_numerica(**condiciones: bool) -> None:
    """Impide una tabla de error si falta una condición esencial.

    Si todas las condiciones son verdaderas, no hace nada. No calcula
    el error: solo deja pasar el paso siguiente.
    """
    faltan = [
        nombre
        for nombre in CONDICIONES_NUMERICAS
        if not condiciones.get(nombre, False)
    ]
    if faltan:
        raise ValueError(
            "Comparación numérica no defendible. Faltan: " + ", ".join(faltan)
        )
