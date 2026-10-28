"""Comparaciones contra números escritos en la propia hoja BES-jun.

El umbral sale de las celdas «Limite minimo», «Cono de eficiencia» y
«Limite maximo» de esa hoja. No se importa un porcentaje de BEP de otra fuente.

Base de frecuencia
------------------
Esos tres límites están escritos en el bloque de la curva a 60 Hz
(p. ej. QF-554H!G56:G58). La propia hoja los lleva a otra frecuencia con
Q(f) = Q(60) * f / 60 (QF-554H!J85:S90, p. ej. J85 = J88*(I85/I88)).
El caudal de operación se mide a la frecuencia de operación de la hoja.
Comparar el caudal de operación con el límite sin escalar mezcla dos bases
de frecuencia. La primera versión de este módulo lo hizo y produjo una
alerta (QF-084, 10301 BFPD a 63 Hz contra 10000 BFPD a 60 Hz) que
desaparece al comparar en la misma base. Se conserva ``escalar=False``
solo para mostrar ese efecto.
"""

from __future__ import annotations

FRECUENCIA_BASE_LIMITES_HZ = 60.0


def limites_a_frecuencia(pozo: dict, escalar: bool = True) -> dict | None:
    """Límites de caudal a la frecuencia de operación, con la relación de la hoja."""
    f = pozo.get("frecuencia_hz")
    f_base = pozo.get("frecuencia_curva_hz") or FRECUENCIA_BASE_LIMITES_HZ
    qmin = pozo.get("limite_minimo_bfpd")
    qcono = pozo.get("cono_eficiencia_bfpd")
    qmax = pozo.get("limite_maximo_bfpd")
    if qmin is None or qmax is None:
        return None
    if escalar:
        if f is None or f_base in (None, 0):
            return None
        razon = f / f_base
    else:
        razon = 1.0
    return {
        "frecuencia_operacion_hz": f,
        "frecuencia_base_hz": f_base,
        "razon_frecuencia": razon,
        "minimo_bfpd": qmin * razon,
        "cono_bfpd": None if qcono is None else qcono * razon,
        "maximo_bfpd": qmax * razon,
    }


def comparar_caudal_con_limites(pozo: dict, escalar: bool = True) -> list[dict]:
    """Devuelve observaciones. Estado de revisión: pendiente.

    escalar=True compara en la misma base de frecuencia (comportamiento válido).
    escalar=False reproduce la comparación directa de la primera versión.
    """
    caudal = pozo.get("caudal_operacion_bfpd")
    limites = limites_a_frecuencia(pozo, escalar=escalar)
    if caudal is None or limites is None:
        return [
            {
                "id": "RC-BES-00",
                "estado_revision": "pendiente",
                "nivel_confianza": "bajo",
                "resultado": "no_evaluable",
                "pozo": pozo.get("pozo"),
                "hoja": pozo.get("hoja"),
                "motivo": "Falta el caudal, la frecuencia de operación o un límite escrito en la hoja.",
            }
        ]
    qmin, qmax = limites["minimo_bfpd"], limites["maximo_bfpd"]
    if qmin > qmax:
        return [
            {
                "id": "RC-BES-00",
                "estado_revision": "pendiente",
                "nivel_confianza": "bajo",
                "resultado": "no_evaluable",
                "pozo": pozo.get("pozo"),
                "hoja": pozo.get("hoja"),
                "motivo": "El límite mínimo escrito supera al máximo. No se clasifica el caudal.",
            }
        ]
    base = {
        "estado_revision": "pendiente",
        "nivel_confianza": "bajo",
        "pozo": pozo.get("pozo"),
        "hoja": pozo.get("hoja"),
        "caudal_bfpd": caudal,
        "limites_a_frecuencia_de_operacion": escalar,
        "frecuencia_operacion_hz": limites["frecuencia_operacion_hz"],
        "limite_minimo_bfpd": qmin,
        "cono_eficiencia_bfpd": limites["cono_bfpd"],
        "limite_maximo_bfpd": qmax,
        "uso_del_limite_maximo_pct": 100.0 * caudal / qmax,
    }
    if caudal > qmax:
        return [
            {
                **base,
                "id": "RC-BES-01",
                "resultado": "por_encima_del_limite_maximo",
                "umbral_bfpd": qmax,
                "fuente_umbral": "celda Limite maximo de la misma hoja"
                + (" escalada por f/60" if escalar else " sin escalar"),
                "sugerencia": "Revisar con el responsable si ese límite aplica a este punto de operación.",
            }
        ]
    if caudal < qmin:
        return [
            {
                **base,
                "id": "RC-BES-02",
                "resultado": "por_debajo_del_limite_minimo",
                "umbral_bfpd": qmin,
                "fuente_umbral": "celda Limite minimo de la misma hoja"
                + (" escalada por f/60" if escalar else " sin escalar"),
                "sugerencia": "Revisar con el responsable si ese límite aplica a este punto de operación.",
            }
        ]
    return [
        {
            **base,
            "id": "RC-BES-03",
            "resultado": "dentro_de_los_limites_escritos",
            "condicion": "limite_minimo <= caudal de operación <= limite_maximo, en la misma base de frecuencia",
        }
    ]
