"""Exporta un cuaderno completo a HTML (nbconvert) y de ahí a PDF Letter (Chrome headless).

Flujo obligatorio: cuaderno .ipynb -> HTML íntegro -> PDF íntegro.
Nada se extrae ni se resume: el HTML contiene todas las celdas de texto, todo el código, todas las salidas
(texto, tablas HTML, imágenes en base64) y las ecuaciones como MathML. No hay recursos remotos ni JavaScript.

Entorno de referencia (Fedora Linux 43): nbconvert 7.17, pandoc (filtro Markdown con MathML), Google Chrome >= 131
(cajas de margen @bottom-center para la numeración), PyMuPDF solo en la verificación.
No modifica el .ipynb ni ningún dato de entrada.
"""

from __future__ import annotations

import html as _html
import re
import subprocess
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter
from pygments.formatters import HtmlFormatter

CHROME = "google-chrome"
COLUMNAS_PARA_APAISAR = 6          # una tabla marcada como ancha va apaisada si tiene >= 6 columnas ...
ANCHO_CARACTER_PT = 4.1                # ancho medido de un carácter de cabecera (Liberation Sans bold 7.6 pt)
ANCHO_UTIL_VERTICAL_PT = 560.0         # ancho útil vertical = 504 pt; la estimación de cabeceras es conservadora (la prueba de recortes decide)
CARACTERES_POR_FILA_PARA_APAISAR = 200  # ... y mucho texto por fila (si no, cabe en vertical ajustando el texto)


def _markdown_a_html(texto: str) -> str:
    """Markdown -> HTML con pandoc. Ecuaciones $..$, $$..$$ y \\(..\\) salen como MathML (sin MathJax remoto)."""
    proc = subprocess.run(
        ["pandoc", "-f", "markdown-smart+tex_math_single_backslash", "-t", "html5", "--mathml"],
        input=texto, text=True, capture_output=True, check=True,
    )
    return proc.stdout


CSS_BASE = """
@page { size: Letter; margin: 0.8in 0.75in 0.85in 0.75in;
  @bottom-center { content: counter(page) " / " counter(pages); font: 8pt "Liberation Sans", sans-serif; color: #555; }
  @top-left { content: "%(titulo)s"; font: 7.5pt "Liberation Sans", sans-serif; color: #777; }
  @top-right { content: "BES-jun · Listo para revisión"; font: 7.5pt "Liberation Sans", sans-serif; color: #777; } }
@page ancho { size: Letter landscape; margin: 0.65in 0.6in 0.7in 0.6in;
  @bottom-center { content: counter(page) " / " counter(pages); font: 8pt "Liberation Sans", sans-serif; color: #555; }
  @top-left { content: "%(titulo)s"; font: 7.5pt "Liberation Sans", sans-serif; color: #777; }
  @top-right { content: "BES-jun · Listo para revisión"; font: 7.5pt "Liberation Sans", sans-serif; color: #777; } }
html { font-family: "Liberation Serif", "DejaVu Serif", serif; font-size: 10.5pt; }
body { margin: 0; line-height: 1.38; color: #111; hyphens: manual; }
.cuaderno { text-align: justify; }
h1, h2, h3, h4 { font-family: "Liberation Sans", "DejaVu Sans", sans-serif; text-align: left; break-after: avoid; page-break-after: avoid; line-height: 1.2; }
h1 { font-size: 19pt; margin: 0 0 0.5em 0; border-bottom: 2px solid #333; padding-bottom: 0.2em; }
h2 { font-size: 13.5pt; margin: 1.2em 0 0.4em 0; border-bottom: 1px solid #aaa; padding-bottom: 0.1em; }
h3 { font-size: 11.5pt; margin: 1em 0 0.3em 0; }
p { margin: 0.45em 0; orphans: 3; widows: 3; }
li { margin: 0.15em 0; }
blockquote { margin: 0.6em 0; padding: 0.3em 0.8em; border-left: 3px solid #999; background: #f6f6f6; text-align: left; }
.portada { break-after: page; page-break-after: always; }
.portada h1 { font-size: 21pt; }
.portada { line-height: 1.3; }
.portada p, .portada li { font-size: 9.8pt; margin: 0.3em 0; }
.portada h2 { font-size: 12pt; margin: 0.8em 0 0.3em 0; }
.portada h1 { margin-bottom: 0.3em; }
.prompt { display: none; }
.input, .output_wrapper { margin: 0.5em 0; }
.input_area { text-align: left; border: 1px solid #c8c8c8; border-left: 4px solid #4c78a8; background: #f7f9fb; padding: 0.3em 0.5em; position: relative; }
.input_area::before { content: "Código"; display: block; font: bold 7pt "Liberation Sans", sans-serif; color: #4c78a8; letter-spacing: 0.06em; margin-bottom: 0.2em; }
.output_area { text-align: left; border-left: 4px solid #8a8a8a; padding: 0.2em 0 0.2em 0.5em; margin-top: 0.3em; }
.output_area::before { content: "Salida"; display: block; font: bold 7pt "Liberation Sans", sans-serif; color: #666; letter-spacing: 0.06em; margin-bottom: 0.15em; }
pre { font-family: "Liberation Mono", "DejaVu Sans Mono", monospace; font-size: 7.4pt; line-height: 1.28; margin: 0;
      white-space: pre-wrap; overflow-wrap: anywhere; word-break: break-word; text-align: left; }
code { font-family: "Liberation Mono", "DejaVu Sans Mono", monospace; font-size: 0.88em; }
table.tabla, .output_html table, table { border-collapse: collapse; width: 100%%; table-layout: auto; font-size: 7.6pt; line-height: 1.22; text-align: left; margin: 0.3em 0 0.5em 0; }
th, td { border: 1px solid #777; padding: 0.15em 0.3em; vertical-align: top; overflow-wrap: anywhere; word-break: break-word; }
th { background: #e8edf2; font-family: "Liberation Sans", sans-serif; font-weight: bold; overflow-wrap: break-word; word-break: normal; }
thead { display: table-header-group; }
tr { break-inside: avoid; page-break-inside: avoid; }
.text_cell_render table { font-size: 8.6pt; }
img { max-width: 100%%; height: auto; display: block; margin: 0.4em auto; break-inside: avoid; page-break-inside: avoid; }
.ancho { page: ancho; }
.ancho table { font-size: 8pt; }
math { font-size: 1.05em; }
math[display="block"] { margin: 0.5em 0; break-inside: avoid; }
.output_stderr pre { color: #8a1c1c; }
%(pygments)s
"""


def _titulo(nb: nbformat.NotebookNode) -> str:
    for celda in nb.cells:
        if celda.cell_type == "markdown":
            for linea in celda.source.splitlines():
                if linea.startswith("# "):
                    return linea[2:].strip()
    return "Cuaderno"


def _envolver_tablas_anchas(cuerpo: str) -> str:
    """Pone en página apaisada las tablas anchas que no caben en vertical sin partir palabras de las cabeceras.

    Una tabla marcada como ancha va apaisada si (a) la suma de las palabras más largas de sus cabeceras no cabe en el
    ancho útil vertical, o (b) tiene muchas columnas y mucho texto por fila. El resto se ajusta en vertical.
    """
    def reemplazo(m: re.Match) -> str:
        tabla = m.group(0)
        if "tabla-ancha" not in tabla[:200]:
            return tabla
        cabeceras = [re.sub(r"<[^>]+>", "", h) for h in re.findall(r'<th class="col_heading[^>]*>(.*?)</th>', tabla, flags=re.S)]
        n_cols = len(cabeceras)
        ancho_min = sum(max(max((len(w) for w in h.split()), default=1) * ANCHO_CARACTER_PT + 7, 20) for h in cabeceras)
        filas = re.findall(r"<tr>.*?</tr>", tabla, flags=re.S)
        texto = re.sub(r"<[^>]+>", "", " ".join(filas[1:]))
        por_fila = len(texto.strip()) / max(len(filas) - 1, 1)
        if ancho_min > ANCHO_UTIL_VERTICAL_PT or (n_cols >= COLUMNAS_PARA_APAISAR and por_fila >= CARACTERES_POR_FILA_PARA_APAISAR):
            return f'<div class="ancho">{tabla}</div>'
        return tabla
    return re.sub(r"<table[^>]*>.*?</table>", reemplazo, cuerpo, flags=re.S)


def html_de_cuaderno(ruta_ipynb: Path) -> str:
    """HTML autocontenido del cuaderno completo."""
    nb = nbformat.read(ruta_ipynb, as_version=4)
    exportador = HTMLExporter(template_name="basic", filters={"markdown2html": _markdown_a_html})
    cuerpo, _ = exportador.from_notebook_node(nb)
    # La primera celda de texto es la portada (título, contexto, propósito, objetivos y alcance; sin código).
    cuerpo = cuerpo.replace('<div class="text_cell_render border-box-sizing rendered_html">',
                            '<div class="text_cell_render border-box-sizing rendered_html portada">', 1)
    cuerpo = _envolver_tablas_anchas(cuerpo)
    # Celdas cortas sin espacios (identificadores como «E-01», «C02b-1») no se parten en dos líneas; el texto no cambia.
    cuerpo = re.sub(r"(<t[dh](?: [^>]*)?)>([^<\s]{1,12})</(t[dh])>", r'\1 style="white-space:nowrap">\2</\3>', cuerpo)
    titulo = _titulo(nb)
    css = CSS_BASE % {"titulo": titulo.replace('"', "'"), "pygments": HtmlFormatter(style="default").get_style_defs(".highlight")}
    return ("<!DOCTYPE html>\n<html lang=\"es\"><head><meta charset=\"utf-8\">"
            f"<title>{_html.escape(titulo)}</title><style>{css}</style></head>"
            f"<body><div class=\"cuaderno\">{cuerpo}</div></body></html>")


def pdf_desde_html(ruta_html: Path, ruta_pdf: Path) -> None:
    """HTML -> PDF con Chrome headless. Falla (no devuelve éxito) si el PDF no se escribe."""
    ruta_pdf.parent.mkdir(parents=True, exist_ok=True)
    if ruta_pdf.exists():
        ruta_pdf.unlink()      # solo el archivo temporal de destino de esta misma exportación
    comando = [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={ruta_pdf}", ruta_html.resolve().as_uri()]
    proc = subprocess.run(comando, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0 or not ruta_pdf.is_file() or ruta_pdf.stat().st_size < 5000:
        raise RuntimeError("Chrome no escribió un PDF válido:\n" + " ".join(comando) + "\n" + proc.stderr[-2000:])


def exportar_cuaderno(ruta_ipynb: Path, carpeta_destino: Path) -> tuple[Path, Path]:
    """Escribe <nombre>.html y <nombre>.pdf en ``carpeta_destino``."""
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    ruta_html = carpeta_destino / f"{ruta_ipynb.stem}.html"
    ruta_pdf = carpeta_destino / f"{ruta_ipynb.stem}.pdf"
    ruta_html.write_text(html_de_cuaderno(ruta_ipynb), encoding="utf-8")
    pdf_desde_html(ruta_html, ruta_pdf)
    return ruta_html, ruta_pdf
