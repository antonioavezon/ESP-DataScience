"""Comprueba si BES-jun podría pasar a ``procesadas``. No lo mueve.

El traslado es un acto manual, posterior a una autorización explícita.
Este módulo no llama a funciones que renombren ni borren el expediente,
aunque todas las comprobaciones salgan bien: el cierre computacional
no es la aprobación operacional, y varias consultas técnicas siguen abiertas.
"""

from __future__ import annotations

from pathlib import Path

from ingesta.leer_bes_jun import raiz_expediente

NOTEBOOKS = (
    "00_inventario_y_fuentes",
    "00_inventario_y_trazabilidad",
    "01_inspeccion_BES_jun",
    "01_inspeccion_y_calidad_datos",
    "02_ecuaciones_y_variables",
    "02_trazabilidad_y_analisis_formulas",
    "03_limpieza_y_mapeo",
    "03_mapeo_y_preparacion_BES_jun",
    "04_calculos_deterministicos",
    "04_modelo_deterministico",
    "05_evaluacion_por_pozo",
    "06_hallazgos_y_reglas_candidatas",
)

ESTADOS = (
    "pendiente",
    "inventariado",
    "en_analisis",
    "analisis_completado",
    "validacion_pendiente",
    "listo_para_cierre",
    "procesado",
    "bloqueado",
)


def comprobar(raiz: Path | None = None) -> dict:
    """Devuelve el estado y la lista de comprobaciones. No modifica archivos."""
    raiz = Path(raiz) if raiz is not None else raiz_expediente()
    checks = []

    def ok(nombre: str, condicion: bool, detalle: str) -> None:
        checks.append({"nombre": nombre, "cumple": bool(condicion), "detalle": detalle})

    ok("expediente_en_en_uso", raiz.parent.name == "en_uso", str(raiz))
    ok("copia_de_trabajo", (raiz / "entrada" / "BES_jun.xlsx").is_file(), "entrada/BES_jun.xlsx")
    ok("doce_notebooks", all((raiz / "notebooks" / f"{n}.ipynb").is_file() for n in NOTEBOOKS), "notebooks/")
    ok("doce_html", all((raiz / "pdf" / "notebooks" / f"{n}.html").is_file() for n in NOTEBOOKS), "pdf/notebooks/*.html")
    ok("doce_pdf", all((raiz / "pdf" / "notebooks" / f"{n}.pdf").is_file() for n in NOTEBOOKS), "pdf/notebooks/*.pdf")
    ok("ficha_maestra", (raiz / "docs" / "ficha_maestra_BES-jun.md").is_file(), "docs/ficha_maestra_BES-jun.md")
    ok("paquete_de_integracion", (raiz / "integracion" / "manifiesto.json").is_file() and (raiz / "integracion" / "reglas.json").is_file(), "integracion/")
    ok("guia_de_integracion", (raiz / "integracion" / "README.md").is_file(), "integracion/README.md")
    ok("informe_markdown", (raiz / "reports" / "informe_analisis_BES-jun.md").is_file(), "reports/")
    ok("registro_de_limitaciones", (raiz / "docs" / "consultas_tecnicas_pendientes.md").is_file(), "CT-01…CT-10 siguen abiertas")
    consultas = (raiz / "docs" / "consultas_tecnicas_pendientes.md").read_text(encoding="utf-8") if (raiz / "docs" / "consultas_tecnicas_pendientes.md").is_file() else ""
    ok("sin_cierre_operacional", "CT-08" in consultas, "mientras CT-08 y el resto sigan abiertas no hay aprobación operacional")
    fallos = [c["nombre"] for c in checks if not c["cumple"]]
    return {
        "dataset_id": "BES-jun",
        "estado_dataset": "validacion_pendiente",
        "estado_reglas": "pendiente_validacion",
        "ubicacion": "datasets/en_uso/BES-jun",
        "puede_moverse_a_procesadas": False,
        "motivo": "El cierre computacional no autoriza el traslado. Faltan la aprobación técnica de las reglas y una autorización explícita de mover la carpeta.",
        "comprobaciones": checks,
        "comprobaciones_fallidas": fallos,
        "movido": False,
    }


def promover(*_args, **_kwargs) -> dict:
    """Punto de entrada reservado. Siempre se niega a mover el expediente."""
    informe = comprobar()
    informe["movido"] = False
    informe["motivo"] = (
        "Este módulo no mueve carpetas. Cuando haya autorización explícita y las consultas técnicas "
        "estén resueltas, el traslado de datasets/en_uso/BES-jun a datasets/procesadas/BES-jun "
        "lo hace una persona, no este código."
    )
    return informe
