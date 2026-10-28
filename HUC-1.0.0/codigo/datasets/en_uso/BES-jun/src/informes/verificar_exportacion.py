"""Verificación automática de la exportación cuaderno -> HTML -> PDF.

No basta con que el PDF exista. Cada cuaderno se verifica en cuatro dimensiones, con errores separados:

* ``contenido``:   la estructura del .ipynb (celdas de texto y de código no vacías, portada sin código, secciones finales).
* ``ejecucion``:   todas las celdas de código ejecutadas, sin salidas de error y sin criterios en «NO CUMPLE».
* ``exportacion``: el HTML contiene, en orden, el texto de cada celda de Markdown, todo el código, todas las salidas
                   (texto y tablas), las imágenes y las ecuaciones; sin recursos remotos ni scripts.
* ``paginacion``:  el PDF es Letter, tiene todo el texto en orden, sin páginas en blanco, sin recortes de texto, tablas
                   ni imágenes fuera del margen, con numeración completa, portada sin código y sin títulos huérfanos.

La comparación de texto trabaja con la secuencia de caracteres alfanuméricos (sin espacios), de modo que los saltos de
línea del PDF dentro de una palabra o de un hash no producen falsos negativos, y exige el **orden** del documento.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

import nbformat
import pymupdf

PORTRAIT = (612.0, 792.0)
LANDSCAPE = (792.0, 612.0)
MARGEN_VERTICAL_IN = 0.75          # margen lateral de @page (pulgadas)
MARGEN_APAISADO_IN = 0.6
TOLERANCIA_PT = 3.0
TROZO = 16                        # caracteres alfanuméricos por trozo de comparación
MIN_PAGINAS = 3


# ------------------------------------------------------------------ utilidades de texto
def _flujo(texto: str) -> str:
    """Solo caracteres alfanuméricos, en minúsculas y normalizados (NFKC)."""
    t = unicodedata.normalize("NFKC", texto).lower()
    return "".join(c for c in t if c.isalnum())


_MATEMATICA = re.compile(r"\$\$.+?\$\$|(?<!\\)\$[^$\n]+?\$|\\\(.+?\\\)|\\\[.+?\\\]", re.S)


def _segmentos_sin_matematica(fuente: str) -> list[str]:
    """Partes de texto de una celda sin sus ecuaciones (cada ecuación corta el texto)."""
    sin_url = re.sub(r"https?://\S+", " ", fuente)
    # Los marcadores de lista («1.», «-», «*») y de cita («>») no son texto del documento: el navegador los dibuja
    # como numeración o viñeta. Los encabezados («## 1. Título») sí conservan su numeración, que es texto.
    limpio = []
    for linea in sin_url.splitlines():
        if not linea.lstrip().startswith("#"):
            linea = re.sub(r"^\s*(?:\d+[.)]|[-*+]|>)\s+", "", linea)
        limpio.append(linea)
    # Cada línea de origen es un segmento independiente: así los marcadores de lista (que el navegador dibuja entre
    # elementos) no cortan una comparación continua.
    segmentos = []
    for linea in limpio:
        segmentos += [s for s in _MATEMATICA.split(linea) if s.strip()]
    return segmentos


def _contar_ecuaciones(fuente: str) -> int:
    return len(_MATEMATICA.findall(fuente))


def _trozos(flujo: str) -> list[str]:
    return [flujo[i:i + TROZO] for i in range(0, len(flujo), TROZO)]


def _comprobar_en_orden(esperados: list[str], documento: str, inicio: int = 0) -> tuple[int, int, int]:
    """Cuenta los trozos esperados encontrados en orden dentro de ``documento``.

    Devuelve (total, faltantes, posicion_final). Un trozo ausente no mueve la posición.
    """
    pos, faltan = inicio, 0
    for trozo in esperados:
        i = documento.find(trozo, pos)
        if i < 0:
            faltan += 1
        else:
            pos = i + len(trozo)
    return len(esperados), faltan, pos


class _TextoHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.partes: list[str] = []
        self._omitir = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "title"):
            self._omitir += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script", "title") and self._omitir:
            self._omitir -= 1

    def handle_data(self, data):
        if not self._omitir:
            self.partes.append(data)


def _texto_html(cuerpo: str) -> str:
    p = _TextoHTML()
    p.feed(cuerpo)
    return " ".join(p.partes)


def _unir(valor) -> str:
    return "".join(valor) if isinstance(valor, list) else (valor or "")


# ------------------------------------------------------------------ elementos esperados del cuaderno
def _partes_markdown(fuente: str) -> list[tuple[str, object]]:
    """Divide una celda Markdown en partes ('t', segmento de texto) y ('c', celdas de una tabla)."""
    partes, texto, tabla = [], [], []

    def cerrar_texto():
        if texto:
            for seg in _segmentos_sin_matematica("\n".join(texto)):
                partes.append(("t", seg))
            texto.clear()

    def cerrar_tabla():
        if tabla:
            celdas = []
            for fila in tabla:
                trozos = [c.strip() for c in fila.strip().strip("|").split("|")]
                if all(re.fullmatch(r":?-{2,}:?", c) for c in trozos if c):
                    continue                                   # fila separadora
                celdas += [_MATEMATICA.sub(" ", c) for c in trozos if c]
            partes.append(("c", celdas))
            tabla.clear()

    for linea in fuente.splitlines():
        if linea.lstrip().startswith("|"):
            cerrar_texto()
            tabla.append(linea)
        else:
            cerrar_tabla()
            texto.append(linea)
    cerrar_tabla()
    cerrar_texto()
    return partes


def _partes_html(cuerpo: str) -> list[tuple[str, object]]:
    """Partes de una salida HTML: texto fuera de tablas y celdas de las tablas, en orden."""
    partes, ultimo = [], 0
    for m in re.finditer(r"<table.*?</table>", cuerpo, flags=re.S):
        fuera = _texto_html(cuerpo[ultimo:m.start()])
        if _flujo(fuera):
            partes.append(("t", fuera))
        celdas = [_texto_html(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", m.group(0), flags=re.S)]
        partes.append(("c", [c for c in celdas if _flujo(c)]))
        ultimo = m.end()
    resto = _texto_html(cuerpo[ultimo:])
    if _flujo(resto):
        partes.append(("t", resto))
    return partes


def _esperado_por_celda(nb) -> list[tuple[str, str, int, list]]:
    """Lista ordenada de (tipo, etiqueta, índice de celda, partes) con partes ('t', texto) o ('c', celdas de tabla)."""
    items = []
    for i, c in enumerate(nb.cells):
        if c.cell_type == "markdown":
            items.append(("markdown", f"celda {i}", i, _partes_markdown(c.source)))
        elif c.cell_type == "code":
            items.append(("código", f"celda {i}", i, [("t", c.source)]))
            for o in c.get("outputs", []):
                if o.output_type == "stream":
                    items.append(("salida", f"celda {i}", i, [("t", _unir(o.get("text")))]))
                elif o.output_type in ("display_data", "execute_result"):
                    datos = o.get("data", {})
                    if "text/html" in datos:
                        items.append(("salida", f"celda {i}", i, _partes_html(_unir(datos["text/html"]))))
                    elif "image/png" in datos:
                        pass                                   # se verifica por conteo de imágenes
                    elif "text/plain" in datos:
                        items.append(("salida", f"celda {i}", i, [("t", _unir(datos["text/plain"]))]))
                elif o.output_type == "error":
                    items.append(("salida", f"celda {i}", i, [("t", "\n".join(o.get("traceback", [])))]))
    return items


def _cubierta_por_trozos(palabra: str, ventana: str, profundidad: int = 3) -> bool:
    """La palabra está en la ventana, entera o partida en hasta ``profundidad`` trozos (salto de línea en medio)."""
    if palabra in ventana:
        return True
    if profundidad <= 1 or len(palabra) < 4:
        return False
    return any(
        palabra[:k] in ventana and _cubierta_por_trozos(palabra[k:], ventana, profundidad - 1)
        for k in range(2, len(palabra) - 1)
    )


def _palabras_en_ventana(celda: str, ventana: str) -> bool:
    """Alternativa para celdas de varias líneas: el PDF intercala las líneas de celdas vecinas de la misma fila.

    Se exige que cada palabra de la celda esté en la ventana de su tabla (entera o partida por un salto de línea).
    Es menos estricta que la comparación contigua, que se intenta siempre primero.
    """
    palabras = [_flujo(w) for w in celda.split()]
    return all(_cubierta_por_trozos(w, ventana) for w in palabras if w)


def _comprobar_documento(nb, flujo: str, tablas_en_orden_estricto: bool) -> tuple[dict, dict, list[str]]:
    """Comprueba que todo el texto esperado aparece en ``flujo`` y en el orden del documento.

    Texto corrido, código y salidas de texto: en orden estricto. Celdas de tabla: si ``tablas_en_orden_estricto`` es
    falso (PDF: Chrome escribe las celdas por columnas), cada celda debe estar dentro de la ventana entre el elemento
    anterior y el siguiente, sin exigir el orden interno de la tabla.
    """
    aplanado = [(tipo, et, clase, carga) for tipo, et, _, partes in _esperado_por_celda(nb) for clase, carga in partes]
    pos = 0
    totales = {"markdown": 0, "código": 0, "salida": 0}
    perdidos = {"markdown": 0, "código": 0, "salida": 0}
    mensajes: list[str] = []
    for k, (tipo, et, clase, carga) in enumerate(aplanado):
        if clase == "t" or tablas_en_orden_estricto:
            segmentos = [carga] if clase == "t" else carga
            for seg in segmentos:
                esperados = _trozos(_flujo(seg))
                tot, falt, pos_n = _comprobar_en_orden(esperados, flujo, pos)
                totales[tipo] += tot
                perdidos[tipo] += falt
                if falt == 0:
                    pos = pos_n
                else:
                    mensajes.append(f"{tipo} de la {et}: {falt} de {tot} trozos de texto no aparecen en orden")
        else:
            limite = len(flujo)
            for tipo2, _, clase2, carga2 in aplanado[k + 1:]:
                if clase2 == "t":
                    siguiente = _trozos(_flujo(carga2))
                    if siguiente:
                        j = flujo.find(siguiente[0], pos)
                        limite = j if j >= 0 else len(flujo)
                        break
            fin_max, falt, tot = pos, 0, 0
            for celda in carga:
                f = _flujo(celda)
                if not f:
                    continue
                tot += 1
                j = flujo.find(f, pos, limite)
                if j >= 0:
                    fin_max = max(fin_max, j + len(f))
                elif not _palabras_en_ventana(celda, flujo[pos:limite]):
                    falt += 1
            totales[tipo] += tot
            perdidos[tipo] += falt
            if falt:
                mensajes.append(f"{tipo} de la {et}: {falt} de {tot} celdas de tabla no aparecen en su posición")
            pos = fin_max
    return totales, perdidos, mensajes


def _titulos(nb) -> list[str]:
    """Encabezados Markdown (# ...) en el orden del cuaderno, en texto plano."""
    salida = []
    for c in nb.cells:
        if c.cell_type != "markdown":
            continue
        for linea in c.source.splitlines():
            m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", linea)
            if m:
                t = re.sub(r"[`*_]", "", m.group(2))
                salida.append(_MATEMATICA.sub("", t).strip())
    return salida


def _n_imagenes(nb) -> tuple[int, int]:
    """(salidas PNG, PNG distintos)."""
    hashes = []
    for c in nb.cells:
        if c.cell_type == "code":
            for o in c.get("outputs", []):
                if o.output_type in ("display_data", "execute_result") and "image/png" in o.get("data", {}):
                    hashes.append(hashlib.sha256(_unir(o["data"]["image/png"]).encode()).hexdigest())
    return len(hashes), len(set(hashes))


def _n_tablas_esperadas(nb) -> int:
    n = 0
    for c in nb.cells:
        if c.cell_type == "markdown":
            bloques = re.findall(r"(?:^\|.*\n?)+", c.source, flags=re.M)
            n += sum(1 for b in bloques if re.search(r"^\|\s*:?-{2,}", b, flags=re.M))
        elif c.cell_type == "code":
            for o in c.get("outputs", []):
                if o.output_type in ("display_data", "execute_result"):
                    n += _unir(o.get("data", {}).get("text/html", "")).count("<table")
    return n


# ------------------------------------------------------------------ verificaciones
def _verificar_contenido(nb, errores: list[str], avisos: list[str]) -> None:
    md = [c for c in nb.cells if c.cell_type == "markdown"]
    co = [c for c in nb.cells if c.cell_type == "code"]
    if not md or not co:
        errores.append("el cuaderno no tiene celdas de texto y de código")
        return
    if any(not c.source.strip() for c in nb.cells):
        errores.append("hay celdas vacías")
    if nb.cells[0].cell_type != "markdown" or not nb.cells[0].source.lstrip().startswith("# "):
        errores.append("la primera celda no es una portada Markdown con título")
    for etiqueta in ("Introducción y contexto", "Objetivo general", "Dominio y alcance", "Fuentes y datos"):
        if etiqueta not in nb.cells[0].source:
            errores.append(f"la portada no contiene la sección «{etiqueta}»")
    texto = "\n".join(c.source for c in md)
    for etiqueta in ("## Limitaciones", "## Referencias", "## Conclusión técnica"):
        if etiqueta not in texto:
            errores.append(f"falta la sección «{etiqueta[3:]}»")
    if "@@" in texto:
        errores.append("quedan marcadores de interpretación sin completar (@@)")
    palabras = sum(len(c.source.split()) for c in md)
    if palabras < 600:
        errores.append(f"desarrollo explicativo insuficiente ({palabras} palabras en celdas de texto)")
    if any(not co_i.source.strip() for co_i in co):
        errores.append("hay celdas de código vacías")


def _verificar_ejecucion(nb, errores: list[str], avisos: list[str]) -> None:
    for i, c in enumerate(nb.cells):
        if c.cell_type != "code":
            continue
        if c.get("execution_count") is None:
            errores.append(f"celda de código {i} sin ejecutar")
        for o in c.get("outputs", []):
            if o.output_type == "error":
                errores.append(f"celda {i}: salida de error {o.get('ename')}")
            if o.output_type == "stream" and o.get("name") == "stderr":
                avisos.append(f"celda {i}: salida por stderr")
            texto = _unir(o.get("text")) if o.output_type == "stream" else _texto_html(_unir(o.get("data", {}).get("text/html", "")))
            if "NO CUMPLE" in texto:
                errores.append(f"celda {i}: hay un criterio de aceptación en «NO CUMPLE»")


def _verificar_html(nb, cuerpo: str, errores: list[str], metricas: dict) -> None:
    flujo = _flujo(_texto_html(cuerpo))
    totales, perdidos, mensajes = _comprobar_documento(nb, flujo, tablas_en_orden_estricto=True)
    errores += [f"HTML: {m}" for m in mensajes]
    metricas["html_trozos"] = totales
    metricas["html_trozos_faltantes"] = perdidos

    # secciones en orden
    esperados = [_flujo(t) for t in _titulos(nb)]
    en_html = [_flujo(_texto_html(m.group(2))) for m in re.finditer(r"<h([1-6])[^>]*>(.*?)</h\1>", cuerpo, flags=re.S)]
    if esperados != en_html:
        errores.append(f"HTML: los encabezados no coinciden en número u orden ({len(esperados)} esperados, {len(en_html)} en el HTML)")
    metricas["encabezados"] = len(esperados)

    # imágenes
    n_png, n_png_distintos = _n_imagenes(nb)
    n_img = len(re.findall(r'<img[^>]+src="data:image/png;base64,', cuerpo))
    metricas.update({"imagenes_esperadas": n_png, "imagenes_en_html": n_img})
    if n_img != n_png:
        errores.append(f"HTML: {n_img} imágenes incrustadas, se esperaban {n_png}")

    # tablas y ecuaciones
    n_tab_esp, n_tab = _n_tablas_esperadas(nb), len(re.findall(r"<table", cuerpo))
    metricas.update({"tablas_esperadas": n_tab_esp, "tablas_en_html": n_tab})
    if n_tab != n_tab_esp:
        errores.append(f"HTML: {n_tab} tablas, se esperaban {n_tab_esp}")
    n_ec_esp = sum(_contar_ecuaciones(c.source) for c in nb.cells if c.cell_type == "markdown")
    n_ec = len(re.findall(r"<math[ >]", cuerpo))
    metricas.update({"ecuaciones_esperadas": n_ec_esp, "ecuaciones_en_html": n_ec})
    if n_ec != n_ec_esp:
        errores.append(f"HTML: {n_ec} ecuaciones renderizadas (MathML), se esperaban {n_ec_esp}")

    # recursos remotos
    for patron, nombre in ((r'<(?:img|script|link|iframe|source)[^>]+(?:src|href)="https?://', "recurso remoto"), (r"@import", "@import"),
                           (r"url\(\s*['\"]?https?://", "url() remota"), (r"<script", "script")):
        if re.search(patron, cuerpo, flags=re.I):
            errores.append(f"HTML: contiene {nombre}")


def _texto_visual(pagina) -> str:
    """Texto de la página en orden visual (bloques ordenados por posición). Chrome escribe el texto de las tablas
    en el flujo del PDF después de los bloques que las siguen, de modo que el orden de extracción no es el visual."""
    bloques = pagina.get_text("blocks", clip=_region_contenido(pagina), sort=True)
    return "\n".join(b[4] for b in bloques if b[6] == 0)


def _region_contenido(pagina) -> "pymupdf.Rect":
    ancho, alto = pagina.rect.width, pagina.rect.height
    if ancho > alto:
        return pymupdf.Rect(0, 44, ancho, alto - 0.7 * 72 + 4)
    return pymupdf.Rect(0, 54, ancho, alto - 0.85 * 72 + 4)


def _verificar_pdf(nb, ruta_pdf: Path, n_palabras_html: int, errores: list[str], avisos: list[str], metricas: dict) -> None:
    doc = pymupdf.open(ruta_pdf)
    n = doc.page_count
    metricas["paginas"] = n
    if n < MIN_PAGINAS:
        errores.append(f"PDF: documento sospechosamente breve ({n} páginas)")
    # tamaño de página
    tamanos = []
    for i, p in enumerate(doc, start=1):
        dims = (round(p.rect.width), round(p.rect.height))
        tamanos.append("apaisada" if dims == (792, 612) else "vertical" if dims == (612, 792) else f"otro {dims}")
        if tamanos[-1].startswith("otro"):
            errores.append(f"PDF: la página {i} no es Letter ({dims})")
    metricas["paginas_apaisadas"] = tamanos.count("apaisada")

    flujos_pagina, texto_total = [], []
    for i, p in enumerate(doc, start=1):
        t = _texto_visual(p)
        flujos_pagina.append(t)
        texto_total.append(t)
        # páginas en blanco
        if len(_flujo(t)) < 25 and not p.get_images():
            errores.append(f"PDF: la página {i} está en blanco o casi vacía")
    flujo = _flujo("\n".join(texto_total))
    metricas["pdf_caracteres_alfanumericos"] = len(flujo)

    # texto completo y en orden
    totales, perdidos, mensajes = _comprobar_documento(nb, flujo, tablas_en_orden_estricto=False)
    errores += [f"PDF: {m}" for m in mensajes]
    metricas["pdf_trozos"] = totales
    metricas["pdf_trozos_faltantes"] = perdidos

    # secciones en orden y títulos huérfanos
    pos = 0
    for t in _titulos(nb):
        f = _flujo(t)
        i = flujo.find(f, pos)
        if i < 0:
            errores.append(f"PDF: el título «{t[:60]}» no aparece en orden")
        else:
            pos = i + len(f)
    titulos = {_flujo(t) for t in _titulos(nb)}
    for i, p in enumerate(doc, start=1):
        bloques = [b for b in p.get_text("blocks", clip=_region_contenido(p)) if b[6] == 0 and b[4].strip()]
        if bloques:
            ultimo = max(bloques, key=lambda b: b[3])
            if _flujo(ultimo[4]) in titulos and i < n:
                errores.append(f"PDF: título huérfano al final de la página {i}: «{ultimo[4].strip()[:60]}»")

    # imágenes
    n_png, n_dist = _n_imagenes(nb)
    n_img_pdf = sum(len(p.get_images(full=True)) for p in doc)
    metricas.update({"imagenes_en_pdf": n_img_pdf})
    if n_img_pdf < n_dist:
        errores.append(f"PDF: {n_img_pdf} imágenes, se esperaban al menos {n_dist}")

    # recortes: texto, tablas (trazos) e imágenes dentro del margen
    recortes = 0
    for i, p in enumerate(doc, start=1):
        ancho, alto = p.rect.width, p.rect.height
        m = (MARGEN_APAISADO_IN if ancho > alto else MARGEN_VERTICAL_IN) * 72
        izq, der = m - TOLERANCIA_PT, ancho - m + TOLERANCIA_PT
        malos = []
        for b in p.get_text("dict", clip=_region_contenido(p))["blocks"]:
            if b.get("type") == 0:
                for l in b["lines"]:
                    for s in l["spans"]:
                        if s["text"].strip() and (s["bbox"][0] < izq or s["bbox"][2] > der):
                            malos.append(("texto", s["text"][:30]))
        for d in p.get_drawings():
            r = d["rect"]
            if r.y0 >= _region_contenido(p).y0 and (r.x0 < izq or r.x1 > der) and r.width > 2:
                malos.append(("trazo", str(r)))
        for info in p.get_image_info():
            r = pymupdf.Rect(info["bbox"])
            if r.x0 < izq or r.x1 > der:
                malos.append(("imagen", str(r)))
        if malos:
            recortes += 1
            errores.append(f"PDF: contenido fuera del margen en la página {i}: {malos[:3]}")
    metricas["paginas_con_recortes"] = recortes

    # numeración
    for i, p in enumerate(doc, start=1):
        pie = p.get_text("text", clip=pymupdf.Rect(0, p.rect.height - 0.6 * 72, p.rect.width, p.rect.height))
        if f"{i} / {n}" not in pie.replace("\n", " "):
            errores.append(f"PDF: la página {i} no muestra su numeración «{i} / {n}»")

    # portada sin código
    portada = _flujo(doc[0].get_text("text", clip=_region_contenido(doc[0])))
    titulo = _flujo(_titulos(nb)[0]) if _titulos(nb) else ""
    if titulo not in portada:
        errores.append("PDF: la primera página no contiene el título")
    for etiqueta in ("Introducciónycontexto", "Objetivogeneral", "Dominioyalcance"):
        if _flujo(etiqueta) not in portada:
            errores.append(f"PDF: la primera página no contiene «{etiqueta}»")
    primera_linea = next((l for c in nb.cells if c.cell_type == "code" for l in c.source.splitlines() if len(_flujo(l)) > 12), "")
    if primera_linea and _flujo(primera_linea) in portada:
        errores.append("PDF: la primera página contiene código")

    # longitud respecto del contenido
    palabras_pdf = len(re.findall(r"\w+", "\n".join(texto_total)))
    metricas["pdf_palabras"] = palabras_pdf
    if n_palabras_html and palabras_pdf < 0.8 * n_palabras_html:
        errores.append(f"PDF: tiene {palabras_pdf} palabras frente a {n_palabras_html} del HTML (documento recortado)")
    doc.close()


def verificar_cuaderno(ruta_ipynb: Path, ruta_html: Path, ruta_pdf: Path) -> dict:
    """Verificación completa de un cuaderno. ``ok`` es verdadero solo si no hay errores en ninguna dimensión."""
    nb = nbformat.read(ruta_ipynb, as_version=4)
    errores = {"contenido": [], "ejecucion": [], "exportacion": [], "paginacion": []}
    avisos: list[str] = []
    metricas: dict = {"celdas": len(nb.cells), "celdas_markdown": sum(c.cell_type == "markdown" for c in nb.cells),
                      "celdas_codigo": sum(c.cell_type == "code" for c in nb.cells),
                      "palabras_explicativas": sum(len(c.source.split()) for c in nb.cells if c.cell_type == "markdown")}
    try:
        nbformat.validate(nb)
    except Exception as e:                                  # noqa: BLE001
        errores["contenido"].append(f"el cuaderno no valida como nbformat: {e}")
    _verificar_contenido(nb, errores["contenido"], avisos)
    _verificar_ejecucion(nb, errores["ejecucion"], avisos)
    cuerpo = ""
    if not ruta_html.is_file() or ruta_html.stat().st_size < 5000:
        errores["exportacion"].append("el HTML no existe o es demasiado pequeño")
    else:
        cuerpo = ruta_html.read_text(encoding="utf-8")
        _verificar_html(nb, cuerpo, errores["exportacion"], metricas)
    if not ruta_pdf.is_file() or ruta_pdf.stat().st_size < 5000:
        errores["paginacion"].append("el PDF no existe o es demasiado pequeño")
    else:
        palabras_html = len(re.findall(r"\w+", _texto_html(cuerpo))) if cuerpo else 0
        _verificar_pdf(nb, ruta_pdf, palabras_html, errores["paginacion"], avisos, metricas)
    return {"cuaderno": ruta_ipynb.stem, "ok": not any(errores.values()), "errores": errores, "avisos": avisos, "metricas": metricas}


def escribir_informe(resultados: list[dict], destino_json: Path, destino_md: Path) -> None:
    destino_json.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    filas = ["| Cuaderno | Contenido | Ejecución | HTML íntegro | PDF íntegro | Páginas | Palabras explicativas | Imágenes | Tablas | Ecuaciones |", "|---|---|---|---|---|---|---|---|---|---|"]
    marca = lambda v: "OK" if not v else f"{len(v)} error(es)"
    for r in resultados:
        m = r["metricas"]
        e = r["errores"]
        filas.append(f"| {r['cuaderno']} | {marca(e['contenido'])} | {marca(e['ejecucion'])} | {marca(e['exportacion'])} | {marca(e['paginacion'])} | "
                     f"{m.get('paginas', '—')} | {m.get('palabras_explicativas', '—')} | {m.get('imagenes_en_pdf', '—')}/{m.get('imagenes_esperadas', '—')} | "
                     f"{m.get('tablas_en_html', '—')}/{m.get('tablas_esperadas', '—')} | {m.get('ecuaciones_en_html', '—')}/{m.get('ecuaciones_esperadas', '—')} |")
    detalle = []
    for r in resultados:
        for dim, lista in r["errores"].items():
            for msg in lista:
                detalle.append(f"- **{r['cuaderno']}** · {dim}: {html.unescape(msg)}")
    texto = "# Verificación de la exportación de cuadernos\n\n" + "\n".join(filas) + "\n\n## Errores\n\n" + ("\n".join(detalle) if detalle else "Ninguno.") + "\n"
    destino_md.write_text(texto, encoding="utf-8")
