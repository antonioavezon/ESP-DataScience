"""Exporta el informe y los cuadernos a PDF tamaño carta.

En Fedora 43 el motor es Google Chrome en modo headless y pandoc para el Markdown.
No usa LaTeX. No modifica el Excel.
"""

from __future__ import annotations

import html
import json
import subprocess
from pathlib import Path

from ingesta.leer_bes_jun import raiz_expediente

def notebooks_del_expediente() -> list[str]:
    raiz = raiz_expediente()
    return sorted(p.name for p in (raiz / "notebooks").glob("*.ipynb"))

CSS = """
@page { size: letter; margin: 0.7in; }
@page ancho { size: letter landscape; margin: 0.55in; }
html { font-family: "Liberation Serif", serif; font-size: 11pt; }
body { margin: 0; text-align: justify; line-height: 1.35; }
h1, h2, h3 { text-align: left; font-family: "Liberation Sans", sans-serif; page-break-after: avoid; }
.portada { page-break-after: always; }
pre, code { font-family: "Liberation Mono", monospace; font-size: 8.5pt; text-align: left; }
pre { white-space: pre-wrap; word-break: break-word; background: #f4f4f4; padding: 0.4em; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; text-align: left; page-break-inside: avoid; }
th, td { border: 1px solid #444; padding: 0.2em 0.35em; vertical-align: top; }
.tabla-ancha { page: ancho; }
img { max-width: 100%; height: auto; }
"""


def exportar() -> list[Path]:
    raise RuntimeError(
        "exportar_pdf.exportar() quedó fuera de uso: reescribía los PDF de los cuadernos con un resumen "
        "y también el PDF del informe. Los cuadernos se exportan con informes.pipeline_cuadernos. "
        "El informe y la ficha se exportan con informes.exportar_documento."
    )
    raiz = raiz_expediente()
    informes = raiz / "pdf" / "informes"
    cuadernos = raiz / "pdf" / "notebooks"
    informes.mkdir(parents=True, exist_ok=True)
    cuadernos.mkdir(parents=True, exist_ok=True)
    salidas = []
    md = raiz / "reports" / "informe_analisis_BES-jun.md"
    html_informe = _html_documento(md_a_html(md.read_text(encoding="utf-8")), portada=False)
    ruta_html = raiz / "reports" / "informe_analisis_BES-jun.html"
    ruta_html.write_text(html_informe, encoding="utf-8")
    pdf_informe = informes / "informe_analisis_BES-jun.pdf"
    _chrome(ruta_html, pdf_informe)
    salidas.append(pdf_informe)
    for nombre in notebooks_del_expediente():
        nb = raiz / "notebooks" / nombre
        destino = cuadernos / nombre.replace(".ipynb", ".pdf")
        pagina = cuadernos / nombre.replace(".ipynb", ".html")
        pagina.write_text(_html_cuaderno(nb), encoding="utf-8")
        _chrome(pagina, destino)
        salidas.append(destino)
    return salidas


def md_a_html(texto: str) -> str:
    proc = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "html"],
        input=texto,
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout


def _html_cuaderno(ruta: Path) -> str:
    nb = json.loads(ruta.read_text(encoding="utf-8"))
    celdas = nb["cells"]
    portada = md_a_html("".join(celdas[0].get("source", [])))
    cuerpo = []
    for celda in celdas[1:]:
        fuente = "".join(celda.get("source", []))
        if celda["cell_type"] == "markdown":
            fragmento = md_a_html(fuente)
            if fuente.count("|") > 16:
                fragmento = f'<div class="tabla-ancha">{fragmento}</div>'
            cuerpo.append(fragmento)
            continue
        cuerpo.append(f"<pre><code>{html.escape(fuente)}</code></pre>")
        for salida in celda.get("outputs", []):
            cuerpo.append(_salida(salida))
    return _html_documento(f'<section class="portada">{portada}</section>' + "\n".join(cuerpo), portada=True)


def _salida(salida: dict) -> str:
    if salida.get("output_type") == "stream":
        texto = salida.get("text", "")
        if isinstance(texto, list):
            texto = "".join(texto)
        return f"<pre><code>{html.escape(texto)}</code></pre>"
    datos = salida.get("data") or {}
    partes = []
    if "image/png" in datos:
        bruto = datos["image/png"]
        if isinstance(bruto, list):
            bruto = "".join(bruto)
        partes.append(f'<img src="data:image/png;base64,{bruto}" alt="Figura">')
    if "text/plain" in datos and salida.get("output_type") != "display_data":
        texto = datos["text/plain"]
        if isinstance(texto, list):
            texto = "".join(texto)
        partes.append(f"<pre><code>{html.escape(texto)}</code></pre>")
    if salida.get("output_type") == "error":
        partes.append("<pre><code>" + html.escape("\n".join(salida.get("traceback", []))) + "</code></pre>")
    return "\n".join(partes)


def _html_documento(cuerpo: str, portada: bool) -> str:
    return (
        "<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'>"
        f"<style>{CSS}</style></head><body>{cuerpo}</body></html>"
    )


def _chrome(html_path: Path, pdf_path: Path) -> None:
    comando = [
        "google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path.resolve().as_uri(),
    ]
    proc = subprocess.run(comando, capture_output=True, text=True)
    if proc.returncode != 0 or not pdf_path.is_file() or pdf_path.stat().st_size < 1000:
        raise RuntimeError(
            "Chrome no escribió el PDF.\n"
            + " ".join(comando)
            + "\n"
            + proc.stderr
        )


def main() -> None:
    for ruta in exportar():
        print(ruta, ruta.stat().st_size)


if __name__ == "__main__":
    main()
