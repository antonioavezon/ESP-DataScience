"""Ejecuta la suite del expediente y escribe un reporte JSON y otro Markdown.

No es un segundo marco de pruebas: llama a pytest. No reescribe reglas ni ecuaciones
si algo falla. Uso, desde la raíz del expediente:

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m evaluacion.autotest
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from evaluacion.contratos import VERSION_CONTRATO
from evaluacion.motor import VERSION_MOTOR
from ingesta.leer_bes_jun import raiz_expediente
from reglas.catalogo import VERSION_CATALOGO


class _Conteo:
    def __init__(self) -> None:
        self.resultados: list[dict] = []

    def pytest_runtest_logreport(self, report) -> None:
        if report.when != "call" and not (report.when == "setup" and report.failed):
            return
        self.resultados.append({
            "nodo": report.nodeid,
            "resultado": report.outcome,
            "duracion_s": round(getattr(report, "duration", 0.0), 4),
            "mensaje": str(report.longrepr)[:500] if report.failed else "",
        })


def ejecutar(raiz: Path | None = None) -> dict:
    raiz = Path(raiz) if raiz is not None else raiz_expediente()
    conteo = _Conteo()
    inicio = time.perf_counter()
    codigo = pytest.main(["-q", "--tb=line", str(raiz / "tests")], plugins=[conteo])
    duracion = round(time.perf_counter() - inicio, 3)
    aprobadas = sum(r["resultado"] == "passed" for r in conteo.resultados)
    fallidas = sum(r["resultado"] == "failed" for r in conteo.resultados)
    omitidas = sum(r["resultado"] == "skipped" for r in conteo.resultados)
    fallos = [r for r in conteo.resultados if r["resultado"] == "failed"]
    informe = {
        "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dataset_id": "BES-jun",
        "version_dataset": "validacion_pendiente",
        "version_contrato": VERSION_CONTRATO,
        "version_motor": VERSION_MOTOR,
        "version_catalogo": VERSION_CATALOGO,
        "total": len(conteo.resultados),
        "aprobadas": aprobadas,
        "fallidas": fallidas,
        "omitidas": omitidas,
        "errores": [{"nodo": r["nodo"], "mensaje": r["mensaje"]} for r in fallos],
        "reglas_afectadas": ["RC-BES-01", "RC-BES-02", "RC-BES-03", "RC-BES-04"],
        "contratos_afectados": [VERSION_CONTRATO],
        "evidencias": [
            "logs/autotest_reporte.json",
            "tests/test_autotest_reglas.py",
            "tests/test_evaluacion_integracion.py",
        ],
        "codigo_salida_pytest": int(codigo),
        "duracion_s": duracion,
        "estado": "aprobado" if codigo == 0 and fallidas == 0 else "con_fallas",
        "pruebas": conteo.resultados,
    }
    logs = raiz / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    (logs / "autotest_reporte.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (logs / "autotest_reporte.md").write_text(_markdown(informe), encoding="utf-8")
    return informe


def _markdown(informe: dict) -> str:
    lineas = [
        "# AutoTest · BES-jun",
        "",
        f"- Fecha: {informe['fecha']}",
        f"- Dataset: {informe['dataset_id']} · estado {informe['version_dataset']}",
        f"- Contrato: {informe['version_contrato']} · Motor: {informe['version_motor']} · Catálogo: {informe['version_catalogo']}",
        f"- Total: {informe['total']} · Aprobadas: {informe['aprobadas']} · Fallidas: {informe['fallidas']} · Omitidas: {informe['omitidas']}",
        f"- Reglas cubiertas: {', '.join(informe['reglas_afectadas'])}",
        f"- Contratos: {', '.join(informe['contratos_afectados'])}",
        f"- Duración: {informe['duracion_s']} s · Estado: **{informe['estado']}**",
        "",
    ]
    fallos = [p for p in informe["pruebas"] if p["resultado"] == "failed"]
    if fallos:
        lineas.append("## Fallos")
        lineas.append("")
        for fallo in fallos:
            lineas.append(f"- `{fallo['nodo']}`: {fallo['mensaje'].splitlines()[0] if fallo['mensaje'] else 'sin mensaje'}")
        lineas.append("")
    else:
        lineas.append("No hubo fallos.")
        lineas.append("")
    return "\n".join(lineas)


def main() -> None:
    informe = ejecutar()
    print(f"{informe['aprobadas']}/{informe['total']} aprobadas · {informe['estado']} · {informe['duracion_s']} s")
    if informe["estado"] != "aprobado":
        raise SystemExit(informe["codigo_salida_pytest"] or 1)


if __name__ == "__main__":
    main()
