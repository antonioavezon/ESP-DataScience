"""Markdown de un documento del expediente → HTML completo → PDF Letter.

No toca los cuadernos. Para esos está ``informes.pipeline_cuadernos``.
No usa el exportador antiguo ``exportar_pdf``, que reescribía los PDF de los cuadernos con un resumen.
"""

from __future__ import annotations

import base64
import re
import subprocess
from pathlib import Path

from informes.exportar_cuadernos import pdf_desde_html

CSS = """
@page { size: Letter; margin: 0.8in 0.75in 0.85in 0.75in;
  @bottom-center { content: counter(page) " / " counter(pages); font: 8pt "Liberation Sans", sans-serif; color: #555; }
  @top-right { content: "BES-jun · validación pendiente"; font: 7.5pt "Liberation Sans", sans-serif; color: #777; } }
html { font-family: "Liberation Serif", serif; font-size: 11pt; }
body { margin: 0; line-height: 1.4; text-align: justify; color: #111; }
h1, h2, h3 { font-family: "Liberation Sans", sans-serif; text-align: left; break-after: avoid; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; text-align: left; }
th, td { border: 1px solid #444; padding: 0.2em 0.35em; vertical-align: top; }
th { background: #e8edf2; }
img { max-width: 100%; height: auto; }
code { font-family: "Liberation Mono", monospace; font-size: 0.9em; }
pre { white-space: pre-wrap; text-align: left; }
"""


def markdown_a_html(texto: str, carpeta: Path | None = None) -> str:
    proc = subprocess.run(
        ["pandoc", "-f", "markdown-smart+tex_math_single_backslash", "-t", "html5", "--mathml"],
        input=texto, text=True, capture_output=True, check=True,
    )
    cuerpo = _incrustar_imagenes(proc.stdout, carpeta) if carpeta is not None else proc.stdout
    return (
        "<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'>"
        f"<style>{CSS}</style></head><body>{cuerpo}</body></html>"
    )


def _incrustar_imagenes(html: str, carpeta: Path) -> str:
    """Sustituye imágenes locales por base64 para que el HTML no dependa de la carpeta ni de la red."""
    def reemplazo(m: re.Match) -> str:
        src = m.group(1)
        if src.startswith(("http://", "https://", "data:")):
            return m.group(0)
        ruta = (carpeta / src).resolve()
        if not ruta.is_file():
            return m.group(0)
        datos = base64.b64encode(ruta.read_bytes()).decode("ascii")
        return f'src="data:image/png;base64,{datos}"'
    return re.sub(r'src="([^"]+)"', reemplazo, html)


def exportar(ruta_md: Path, ruta_html: Path, ruta_pdf: Path) -> None:
    """Escribe el HTML y, desde ese HTML, el PDF. Falla si Chrome no produce el PDF."""
    ruta_html.parent.mkdir(parents=True, exist_ok=True)
    ruta_html.write_text(markdown_a_html(ruta_md.read_text(encoding="utf-8"), ruta_md.parent), encoding="utf-8")
    pdf_desde_html(ruta_html, ruta_pdf)
