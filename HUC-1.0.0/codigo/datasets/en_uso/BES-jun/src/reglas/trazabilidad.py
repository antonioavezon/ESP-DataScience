"""Correspondencia revisada entre cada regla y su fundamento.

La existencia de un identificador no basta: esta tabla dice qué consulta
corresponde y cuál no. La prueba la compara con el catálogo.
"""

from __future__ import annotations

# Revisada contra docs/consultas_tecnicas_pendientes.md (2026-10-20).
# CT-06: si la tabla de seis puntos y la columna EFF son de fabricante.
# CT-08: si Q ∝ f y head ∝ f² valen para estas bombas.
# CT-09: qué diferencia entre caudal calculado y medido sería aceptable.
# CT-09 no fundamenta el BEP ni el «Cono de eficiencia».
CORRESPONDENCIA: dict[str, dict] = {
    "RC-BES-01": {
        "consultas": ("CT-06", "CT-08"),
        "variables": ("caudal_operacion_bfpd", "frecuencia_hz", "limite_maximo_bfpd", "frecuencia_curva_hz"),
        "ecuaciones": ("F-26-afinidad",),
        "modelos": (),
        "porque": "El máximo está escrito en el bloque de la curva (CT-06) y se escala con la afinidad no validada (CT-08).",
    },
    "RC-BES-02": {
        "consultas": ("CT-06", "CT-08"),
        "variables": ("caudal_operacion_bfpd", "frecuencia_hz", "limite_minimo_bfpd", "frecuencia_curva_hz"),
        "ecuaciones": ("F-26-afinidad",),
        "modelos": (),
        "porque": "El mínimo tiene el mismo origen y el mismo escalamiento que el máximo.",
    },
    "RC-BES-03": {
        "consultas": ("CT-06", "CT-08"),
        "variables": ("caudal_operacion_bfpd", "frecuencia_hz", "limite_minimo_bfpd", "limite_maximo_bfpd", "frecuencia_curva_hz"),
        "ecuaciones": ("F-26-afinidad",),
        "modelos": (),
        "porque": "Estar entre los dos números de la hoja no aprueba la curva ni la afinidad.",
    },
    "RC-BES-04": {
        "consultas": ("CT-06",),
        "variables": ("cono_eficiencia_bfpd",),
        "ecuaciones": (),
        "modelos": (),
        "porque": "La regla habla de eficiencia y de BEP. Eso es CT-06. CT-09 es la tolerancia entre caudal calculado y medido, y no se le asigna.",
    },
}
