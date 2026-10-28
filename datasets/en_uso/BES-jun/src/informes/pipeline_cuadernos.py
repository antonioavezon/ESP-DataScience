"""Orquestador: descubre, valida, (reconstruye y ejecuta), exporta a HTML y PDF, verifica e informa.

Uso (Fedora Linux 43, desde la raíz del expediente; usar el intérprete del entorno virtual):

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m informes.pipeline_cuadernos [opciones]

Opciones:
    --construir   regenera TODOS los .ipynb desde ``informes.cuadernos`` (descarta las salidas; los originales están en
                  ``logs/respaldo_previo_a_auditoria/``)
    --ejecutar    ejecuta cada cuaderno con el kernel ``huc-vesp`` (el de trazabilidad va al final, para leer el estado final)
    --solo N ...  procesa solo los cuadernos cuyo nombre contenga N (por ejemplo ``--solo 05 06``)

Reglas:
* Las exportaciones nuevas se escriben primero en ``logs/exportacion_staging/``. Solo los cuadernos cuyo HTML y PDF
  superan **todas** las verificaciones reemplazan a los de ``pdf/notebooks/``; si uno falla, se conserva el anterior.
* No modifica ``pdf/informes/informe_analisis_BES-jun.pdf`` (se registra su huella antes y después).
* El código de salida es 0 solo si todos los cuadernos procesados pasan todas las verificaciones.
* Los errores se separan en: contenido, ejecución, exportación (HTML) y paginación (PDF).
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import time
from pathlib import Path

import nbformat

from ingesta.leer_bes_jun import raiz_expediente
from informes.exportar_cuadernos import exportar_cuaderno
from informes.verificar_exportacion import escribir_informe, verificar_cuaderno

ULTIMO = "00_inventario_y_trazabilidad"        # lee el estado de los demás: se ejecuta al final
ESPERADOS = 12


def _sha(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def descubrir(raiz: Path, solo: list[str]) -> list[Path]:
    todos = sorted((raiz / "notebooks").glob("*.ipynb"))
    return [p for p in todos if not solo or any(s in p.stem for s in solo)]


def ejecutar(ruta: Path) -> str | None:
    """Ejecuta el cuaderno en el sitio. Devuelve un mensaje de error o None."""
    comando = [str(Path(sys.executable).parent / "jupyter"), "nbconvert", "--to", "notebook", "--execute", "--inplace",
               "--ExecutePreprocessor.timeout=900", str(ruta)]
    proc = subprocess.run(comando, capture_output=True, text=True, cwd=ruta.parent)
    if proc.returncode != 0:
        return (proc.stderr or proc.stdout)[-1500:]
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--construir", action="store_true")
    ap.add_argument("--ejecutar", action="store_true")
    ap.add_argument("--solo", nargs="*", default=[])
    a = ap.parse_args(argv)

    raiz = raiz_expediente()
    informe_pdf = raiz / "pdf" / "informes" / "informe_analisis_BES-jun.pdf"
    sha_informe_antes = _sha(informe_pdf) if informe_pdf.is_file() else None
    inicio = time.time()

    if a.construir:
        from informes.construir_cuadernos import main as construir
        print("== Reconstruyendo cuadernos desde informes.cuadernos")
        construir([])

    cuadernos = descubrir(raiz, a.solo)
    if not a.solo and len(cuadernos) != ESPERADOS:
        print(f"!! Se esperaban {ESPERADOS} cuadernos y hay {len(cuadernos)}")
        return 1
    print(f"== {len(cuadernos)} cuadernos descubiertos")

    errores_previos: dict[str, list[str]] = {}
    if a.ejecutar:
        orden = [p for p in cuadernos if p.stem != ULTIMO] + [p for p in cuadernos if p.stem == ULTIMO]
        for p in orden:
            t0 = time.time()
            err = ejecutar(p)
            print(f"   ejecutado {p.stem}: {'ERROR' if err else 'ok'} ({time.time() - t0:.0f} s)")
            if err:
                errores_previos[p.stem] = [err]

    staging = raiz / "logs" / "exportacion_staging"
    destino = raiz / "pdf" / "notebooks"
    staging.mkdir(parents=True, exist_ok=True)
    resultados, promovidos = [], []
    for p in cuadernos:
        print(f"== Exportando y verificando {p.stem}")
        pendientes = errores_previos.get(p.stem, [])
        try:
            nbformat.validate(nbformat.read(p, as_version=4))
            ruta_html, ruta_pdf = exportar_cuaderno(p, staging)
            r = verificar_cuaderno(p, ruta_html, ruta_pdf)
        except Exception as e:                                         # noqa: BLE001
            r = {"cuaderno": p.stem, "ok": False, "avisos": [], "metricas": {},
                 "errores": {"contenido": [], "ejecucion": [], "exportacion": [f"fallo al exportar: {type(e).__name__}: {e}"], "paginacion": []}}
            ruta_html = ruta_pdf = None
        if pendientes:
            r["errores"]["ejecucion"] = [f"fallo de ejecución: {m}" for m in pendientes] + r["errores"]["ejecucion"]
            r["ok"] = False
        resultados.append(r)
        if r["ok"] and ruta_html and ruta_pdf:
            destino.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ruta_html, destino / ruta_html.name)
            shutil.copy2(ruta_pdf, destino / ruta_pdf.name)
            ruta_html.unlink()
            ruta_pdf.unlink()
            promovidos.append(p.stem)
        n_err = sum(len(v) for v in r["errores"].values())
        print(f"   {'OK' if r['ok'] else 'FALLA'} · {n_err} errores · {r['metricas'].get('paginas', '—')} páginas")

    sha_informe_despues = _sha(informe_pdf) if informe_pdf.is_file() else None
    escribir_informe(resultados, raiz / "logs" / "verificacion_exportacion.json", raiz / "logs" / "verificacion_exportacion.md")
    intacto = sha_informe_antes == sha_informe_despues
    ok = all(r["ok"] for r in resultados) and intacto
    print(f"== Promovidos a pdf/notebooks/: {len(promovidos)} de {len(cuadernos)} · informe PDF intacto: {'sí' if intacto else 'NO'} · {time.time() - inicio:.0f} s")
    print("== RESULTADO:", "ÉXITO" if ok else "CON ERRORES (ver logs/verificacion_exportacion.md)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
