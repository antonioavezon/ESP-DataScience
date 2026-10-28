"""Manifiesto de la versión de software de BES-jun, calculado sobre los archivos.

No incluye su propio hash ni el del informe de cierre que lo cita. Así no hay
una referencia circular. Los conteos de pruebas se leen del último AutoTest.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from evaluacion.contratos import VERSION_CONTRATO, VERSION_MOTOR, VERSION_SOFTWARE
from evaluacion.motor import MODELOS
from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO, raiz_expediente
from reglas.catalogo import REGLAS, VERSION_CATALOGO


ARTEFACTOS = (
    "entrada/BES_jun.xlsx",
    "integracion/contrato_entrada.schema.json",
    "integracion/contrato_salida.schema.json",
    "integracion/reglas.json",
    "integracion/ejemplos/solicitud_qf084.json",
    "integracion/ejemplos/resultado_qf084.json",
    "reports/informe_analisis_BES-jun.md",
    "pdf/informes/informe_analisis_BES-jun.pdf",
    "docs/ficha_maestra_BES-jun.md",
)


def construir(raiz: Path | None = None) -> dict:
    raiz = Path(raiz) if raiz is not None else raiz_expediente()
    reporte = {}
    ruta_reporte = raiz / "logs" / "autotest_reporte.json"
    if ruta_reporte.is_file():
        reporte = json.loads(ruta_reporte.read_text(encoding="utf-8"))
    notebooks = sorted((raiz / "notebooks").glob("*.ipynb"))
    htmls = sorted((raiz / "pdf" / "notebooks").glob("*.html"))
    pdfs = sorted((raiz / "pdf" / "notebooks").glob("*.pdf"))
    huellas_artefactos = {}
    for relativo in (*ARTEFACTOS, *(f"notebooks/{p.name}" for p in notebooks), *(f"pdf/notebooks/{p.name}" for p in pdfs)):
        ruta = raiz / relativo
        if ruta.is_file():
            huellas_artefactos[relativo] = hashlib.sha256(ruta.read_bytes()).hexdigest()
    excel = huellas(COPIA_TRABAJO)
    documento = {
        "dataset_id": "BES-jun",
        "estado_dataset": "validacion_pendiente",
        "ubicacion": "datasets/en_uso/BES-jun",
        "version_software": VERSION_SOFTWARE,
        "version_contrato": VERSION_CONTRATO,
        "version_motor": VERSION_MOTOR,
        "version_catalogo": VERSION_CATALOGO,
        "versiones_modelos": {m["id"]: m["version"] for m in MODELOS},
        "fecha_construccion": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sha256_excel": excel["sha256"],
        "bytes_excel": excel["bytes"],
        "notebooks": len(notebooks),
        "html_notebooks": len(htmls),
        "pdf_notebooks": len(pdfs),
        "reglas": [r["id"] for r in REGLAS],
        "reglas_aprobadas": [r["id"] for r in REGLAS if r["aprobada_para_uso_operacional"]],
        "estado_cientifico_reglas": {r["id"]: r["estado_validacion"] for r in REGLAS},
        "pruebas_total": reporte.get("total"),
        "pruebas_aprobadas": reporte.get("aprobadas"),
        "pruebas_fallidas": reporte.get("fallidas"),
        "pruebas_omitidas": reporte.get("omitidas"),
        "autotest_fecha": reporte.get("fecha"),
        "autotest_estado": reporte.get("estado"),
        "cierre_tecnico_software": reporte.get("estado") == "aprobado",
        "aprobacion_operacional": False,
        "limitaciones": [
            "CT-01 a CT-10 abiertas",
            "P-14 abierta",
            "Ninguna regla aprobada para uso operacional",
            "La reproducción del Excel no es validación física independiente",
        ],
        "sha256_artefactos": huellas_artefactos,
        "no_incluye_su_propio_hash": True,
    }
    (raiz / "integracion" / "manifiesto_version.json").write_text(
        json.dumps(documento, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    (raiz / "docs" / "manifiesto_version_BES-jun.md").write_text(_markdown(documento), encoding="utf-8")
    return documento


def _markdown(documento: dict) -> str:
    lineas = [
        "# Manifiesto de versión · BES-jun",
        "",
        "Generado por `integracion.manifiesto_version` a partir de los archivos y del último `logs/autotest_reporte.json`.",
        "Este archivo no entra en la tabla de hashes. El informe de cierre tampoco, para no cerrar un ciclo.",
        "",
        f"- Dataset: {documento['dataset_id']} · {documento['estado_dataset']} · `{documento['ubicacion']}`",
        f"- Software {documento['version_software']} · contrato {documento['version_contrato']} · motor {documento['version_motor']} · catálogo {documento['version_catalogo']}",
        f"- Modelos: {', '.join(f'{k} {v}' for k, v in documento['versiones_modelos'].items())}",
        f"- Fecha: {documento['fecha_construccion']}",
        f"- Excel SHA-256: `{documento['sha256_excel']}` ({documento['bytes_excel']} bytes)",
        f"- Cuadernos: {documento['notebooks']} · HTML: {documento['html_notebooks']} · PDF: {documento['pdf_notebooks']}",
        f"- Reglas: {', '.join(documento['reglas'])}. Aprobadas: {documento['reglas_aprobadas'] or 'ninguna'}.",
        f"- AutoTest: {documento['pruebas_aprobadas']}/{documento['pruebas_total']} aprobadas, {documento['pruebas_fallidas']} fallidas, {documento['pruebas_omitidas']} omitidas. Estado: {documento['autotest_estado']}.",
        f"- Cierre técnico del software: {documento['cierre_tecnico_software']}. Aprobación operacional: {documento['aprobacion_operacional']}.",
        "",
        "## Hashes",
        "",
        "| Archivo | SHA-256 |",
        "|---|---|",
    ]
    for ruta, huella in documento["sha256_artefactos"].items():
        lineas.append(f"| `{ruta}` | `{huella}` |")
    lineas += ["", "## Limitaciones", ""]
    for texto in documento["limitaciones"]:
        lineas.append(f"- {texto}")
    lineas.append("")
    return "\n".join(lineas)


def main() -> None:
    documento = construir()
    print(documento["version_software"], documento["pruebas_aprobadas"], documento["sha256_excel"])


if __name__ == "__main__":
    main()
