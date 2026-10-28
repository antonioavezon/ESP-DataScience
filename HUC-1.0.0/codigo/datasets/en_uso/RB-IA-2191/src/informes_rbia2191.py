"""Construye, ejecuta y exporta los cuadernos de RB-IA-2191. No toca BES-jun ni RB-1521."""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

RAIZ = Path(__file__).resolve().parents[1]
NOTEBOOKS = RAIZ / "notebooks"
PDFS = RAIZ / "pdf" / "notebooks"

PREAMBULO = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))
"""


def _cuaderno(celdas: list[tuple[str, str]]) -> nbformat.NotebookNode:
    nb = new_notebook(cells=[
        new_markdown_cell(texto) if tipo == "md" else new_code_cell(texto)
        for tipo, texto in celdas
    ])
    nb.metadata.kernelspec = {
        "display_name": "Python (HUC VESP)",
        "language": "python",
        "name": "huc-vesp",
    }
    return nb


def construir() -> list[Path]:
    NOTEBOOKS.mkdir(parents=True, exist_ok=True)
    escritos = []
    for nombre, celdas in CUADERNOS:
        ruta = NOTEBOOKS / nombre
        nbformat.write(_cuaderno(celdas), ruta)
        escritos.append(ruta)
    return escritos


def ejecutar(rutas: list[Path]) -> None:
    for ruta in rutas:
        nb = nbformat.read(ruta, as_version=4)
        cliente = NotebookClient(
            nb,
            kernel_name="huc-vesp",
            resources={"metadata": {"path": str(RAIZ)}},
            timeout=120,
        )
        cliente.execute()
        nbformat.write(nb, ruta)


def exportar(rutas: list[Path]) -> None:
    bes = RAIZ.parents[0] / "BES-jun" / "src"
    sys.path.insert(0, str(bes))
    from informes.exportar_cuadernos import html_de_cuaderno, pdf_desde_html

    PDFS.mkdir(parents=True, exist_ok=True)
    for ruta in rutas:
        html = html_de_cuaderno(ruta).replace(
            "BES-jun · Listo para revisión",
            "RB-IA-2191 · Serie diaria",
        )
        destino_html = PDFS / f"{ruta.stem}.html"
        destino_pdf = PDFS / f"{ruta.stem}.pdf"
        destino_html.write_text(html, encoding="utf-8")
        pdf_desde_html(destino_html, destino_pdf)


CUADERNOS = [
    ("00_inventario_y_fuentes.ipynb", [
        ("md", """# Inventario y fuentes de RB-IA-2191

**Dataset:** RB-IA-2191 · **Expediente:** `datasets/en_uso/RB-IA-2191` · **Cuaderno:** 00 · **Tema:** procedencia del libro

## Introducción

RB-IA-2191 es el dataset D2 del tablero de asesor-esp. Hasta esta investigación el expediente permanecía en `en_espera`, con `entrada/` vacía, y la aplicación no abría el `.xlsx`. La única copia íntegra disponible estaba en `fuentes/originales/RB-IA-2191-Data.xlsx`. Este cuaderno fija la identidad binaria del archivo antes de interpretar columnas o caudales.

## Objetivos

El objetivo general es establecer una fuente única y verificable. Los objetivos específicos son calcular el SHA-256 de la copia de trabajo y del original, comprobar igualdad de bytes, y registrar tamaño y formato sin reescribir el libro.

## Metodología

La comparación es binaria con `hashlib.sha256`. No se ejecutan macros ni se pide a Excel que recalcule. La ruta de trabajo es `entrada/RB-IA-2191-Data.xlsx`. La ruta de referencia es `fuentes/originales/RB-IA-2191-Data.xlsx`. Si los hashes difieren, el resto de la investigación carece de fuente única.

## Alcance

Este cuaderno no describe pozos, unidades ni fórmulas. Solo responde si el archivo que se leerá es el entregado por los especialistas.
"""),
        ("code", PREAMBULO + """
from rbia2191_lectura import HASH_ORIGINAL, huella, ruta_entrada
original = Path.cwd().parents[2] / "fuentes" / "originales" / "RB-IA-2191-Data.xlsx"
trabajo = ruta_entrada()
print("bytes trabajo", trabajo.stat().st_size)
print("bytes original", original.stat().st_size)
print("sha trabajo", huella(trabajo))
print("sha original", huella(original))
print("coincide con el registro", huella(trabajo) == HASH_ORIGINAL == huella(original))
print("mismos bytes", trabajo.read_bytes() == original.read_bytes())
"""),
        ("md", """## Resultados e interpretación

La copia de trabajo y el original pesan 15491 bytes y comparten el SHA-256 `908149f26e7560dc6bce75dc0268560e93a05d88b685218856b738dea39d9f08`. La lectura posterior puede atribuirse a ese archivo. El original no se modificó al copiarlo.

## Conclusión

La fuente queda identificada. El cuaderno siguiente puede abrir la hoja sin ambigüedad de versión.
"""),
    ]),
    ("01_estructura_y_calidad.ipynb", [
        ("md", """# Estructura y calidad de la serie RB-IA-2191

**Dataset:** RB-IA-2191 · **Cuaderno:** 01 · **Tema:** geometría de la tabla y continuidad temporal

## Introducción

BES-jun organiza varios pozos en hojas de diseño. RB-1521 es una serie diaria larga sin código de pozo interno. RB-IA-2191 también es una serie temporal, pero más corta y en formato `.xlsx`. Tratarla como un inventario multi-pozo o como una réplica de RB-1521 sería un error de lectura.

## Objetivos

Describir la geometría real del libro, comprobar la continuidad de las fechas y separar columnas constantes de columnas variables.

## Metodología

`openpyxl` con `data_only=True` entrega el valor almacenado. Las celdas vacías permanecen como ausencia. La continuidad se juzga por la diferencia, en días, entre fechas consecutivas. No se imputan huecos.

## Fundamento

Una serie diaria continua permite fijar un día de referencia. Una serie con huecos obligaría a decidir si el hueco es parada o registro perdido; esa decisión no se toma aquí.
"""),
        ("code", PREAMBULO + """
from collections import Counter
from rbia2191_lectura import fecha_iso, leer_serie
serie = leer_serie()
fechas = [fila["FECHA"] for fila in serie]
deltas = Counter((fechas[i] - fechas[i-1]).days for i in range(1, len(fechas)))
print("filas", len(serie))
print("desde", fecha_iso(fechas[0]), "hasta", fecha_iso(fechas[-1]))
print("deltas", dict(deltas))
constantes = {}
variables = {}
for clave in serie[0]:
    if clave == "FECHA":
        continue
    presentes = [fila[clave] for fila in serie if fila[clave] is not None]
    unicos = set(presentes)
    if len(unicos) == 1:
        constantes[clave] = presentes[0]
    else:
        variables[clave] = len(unicos)
print("constantes", sorted(constantes))
print("variables (n únicos)", variables)
"""),
        ("md", """## Resultados

Hay una sola hoja, `Hoja1`, con 28 filas de datos (2020-05-02 a 2020-05-29) y 25 columnas. El salto entre fechas consecutivas es siempre un día.

Permanecen constantes BFPD, BWPD, BOPD, HZ, P_Sensor, H, BSW, PWF, Volt_m, Amp_m, API, T_Yac, GE_W, P_cas, Visco_f, FP y PIP. Varían Sum, THP, P_SUT, Pbomba, Eff_b, Porc_Load y Eff_m.

## Interpretación

El libro describe una serie de un solo conjunto operativo. El nombre `RB-IA-2191` identifica el expediente; el archivo no trae otro código de pozo. No hay columna de marca de bomba.

## Restricción

Que una columna sea constante no demuestra que sea un parámetro de diseño independiente. Solo demuestra que el archivo la repite. Las columnas variables sin fórmula visible no se recalculan en el motor.

## Conclusión

La estructura útil es una tabla diaria 28×25, continua, con un bloque de caudales constantes y un bloque de magnitudes derivadas almacenadas sin expresión.
"""),
    ]),
    ("02_variables_y_unidades.ipynb", [
        ("md", """# Variables y unidades de RB-IA-2191

**Dataset:** RB-IA-2191 · **Cuaderno:** 02 · **Tema:** catálogo de columnas y dominio numérico

## Introducción

Los encabezados no declaran unidades. Asignar «psi» a PIP o «ft» a H porque el nombre lo sugiere adelantaría una convención que la celda no escribe. La identidad verificable `BOPD = BFPD − BWPD` solo exige coherencia dimensional entre tres caudales.

## Objetivos

Inventariar las 25 columnas, justificar la unidad de trabajo de BFPD/BWPD/BOPD y documentar el dominio de BSW sin usarlo como factor.

## Metodología

Se clasifican columnas constantes y variables. Para BSW se observa el intervalo. Para los caudales se conserva BFPD como unidad de trabajo del proyecto, dejando explícito que el encabezado no la imprime.

## Fundamento

Si BSW fuera un porcentaje escrito como 97,2, el valor 0,972 no cabría en ese supuesto. El dominio [0, 1] sugiere fracción, pero eso no autoriza a imponer \(BWPD = BFPD \\times BSW\) cuando el archivo no la cumple.
"""),
        ("code", PREAMBULO + """
from rbia2191_lectura import leer_serie
serie = leer_serie()
bsw = [fila["BSW"] for fila in serie]
print("BSW min", min(bsw), "max", max(bsw))
print("todos entre 0 y 1", all(0 <= v <= 1 for v in bsw))
print("BFPD", {fila["BFPD"] for fila in serie})
print("BWPD", {fila["BWPD"] for fila in serie})
print("BOPD", {fila["BOPD"] for fila in serie})
print("HZ", {fila["HZ"] for fila in serie})
"""),
        ("md", """## Resultados

BSW es constante 0,972 (fracción). BFPD = 5180, BWPD = 5099,4, BOPD ≈ 80,6, HZ = 72,3 en las 28 filas. El catálogo que entra al simulador tiene dos mandos: BFPD y BWPD. El resto se conserva como valor almacenado.

## Interpretación

El motor no ofrece PIP, Sum ni eficiencias como controles, porque no hay expresión verificada que las consuma o produzca.

## Conclusión

La unidad de trabajo de los caudales es BFPD. BSW se documenta como fracción almacenada, no como entrada del cálculo.
"""),
    ]),
    ("03_identidades_numericas.ipynb", [
        ("md", """# Identidades numéricas en RB-IA-2191

**Dataset:** RB-IA-2191 · **Cuaderno:** 03 · **Tema:** qué relación cierra con las celdas

## Introducción

A diferencia de RB-1521, este libro sí deja una fórmula de Excel visible: en cada fila, la columna D (BOPD) contiene `=Bn-Cn`. Esa es la única expresión recuperable. Se contrastan dos candidatas:

1. \(BOPD = BFPD - BWPD\) (declarada en Excel).
2. \(BWPD = BFPD \\times BSW\) (sugerida por el nombre BSW; usada en RB-1521, no trasladable sin prueba).

## Objetivos

Medir en cuántos días cierra cada candidata y decidir qué entra al motor.

## Metodología

Se recalcula cada identidad con tolerancia \(10^{-9}\) (caudales) o \(10^{-6}\) (producto BSW) y se cuenta el número de filas exactas. Además se listan las fórmulas crudas de la columna BOPD.
"""),
        ("code", PREAMBULO + """
from rbia2191_lectura import formulas_bopd, leer_serie
from rbia2191_particion import bsw_reproduce_bwpd, contar_identidades, identidad_exacta
serie = leer_serie()
print("BOPD=BFPD-BWPD", contar_identidades(serie), "/", len(serie))
print("BSW*BFPD=BWPD", sum(1 for f in serie if bsw_reproduce_bwpd(f)), "/", len(serie))
diffs = [abs(float(f["BFPD"]) * float(f["BSW"]) - float(f["BWPD"])) for f in serie]
print("max |BFPD*BSW - BWPD|", max(diffs))
print("fórmulas BOPD únicas", sorted(set(formulas_bopd())))
assert all(identidad_exacta(f) for f in serie)
"""),
        ("md", """## Resultados

`BOPD = BFPD − BWPD` cierra en 28/28 días. Las fórmulas crudas son del patrón `=B2-C2`, …, `=B29-C29`.  
`BFPD × BSW` no reproduce BWPD: la diferencia absoluta es ≈ 64,44 BFPD en todas las filas. Por tanto BSW no es el factor de partición de este libro.

## Interpretación

Reutilizar la partición de RB-1521 aquí falsificaría el archivo. El motor implementa solo la identidad que Excel declara.

## Conclusión

La identidad verificable es BOPD. BSW queda fuera del cálculo determinístico.
"""),
    ]),
    ("04_calculo_bopd.ipynb", [
        ("md", """# Cálculo determinístico BOPD

**Dataset:** RB-IA-2191 · **Cuaderno:** 04 · **Tema:** implementación y escenario simulado

## Introducción

El módulo `rbia2191_particion.particionar` reproduce \(BOPD = BFPD - BWPD\). El motor `evaluacion.motor.evaluar_solicitud` usa el día de referencia (2020-05-02) y admite sobrescribir BFPD y BWPD para simulación, sin escribir el Excel.

## Objetivos

Verificar el día de referencia, un escenario alterado y el rechazo de entradas ajenas.

## Metodología

Se llama al motor con variables vacías y con un par (BFPD, BWPD) distinto. Se comprueba `coincidencia_dia_referencia` y la ausencia de magnitudes inventadas de bomba.
"""),
        ("code", PREAMBULO + """
from evaluacion.motor import evaluar_solicitud
base = evaluar_solicitud({"dataset_id": "RB-IA-2191", "pozo_id": "RB-IA-2191", "variables": []})
print(base["estado_evaluacion"], base["fecha_referencia"], base["coincidencia_dia_referencia"])
print(base["modelos"][0]["valores"])
sim = evaluar_solicitud({
    "dataset_id": "RB-IA-2191",
    "pozo_id": "RB-IA-2191",
    "variables": [
        {"nombre": "bfpd", "valor": 5100, "unidad": "BFPD"},
        {"nombre": "bwpd", "valor": 5000, "unidad": "BFPD"},
    ],
})
print("sim bopd", sim["modelos"][0]["valores"]["bopd"], "coincide", sim["coincidencia_dia_referencia"])
malo = evaluar_solicitud({"pozo_id": "RB-IA-2191", "variables": [{"nombre": "bsw", "valor": 0.9, "unidad": "fracción"}]})
print("rechazo bsw", malo["estado_evaluacion"])
"""),
        ("md", """## Resultados

El día de referencia reproduce BOPD ≈ 80,6 BFPD con `resultados_sin_regla=True`. El escenario 5100/5000 produce BOPD = 100 y deja de coincidir con la fila. Una variable `bsw` se rechaza: no entra en este expediente.

## Conclusión

El cálculo expuesto a HUC es deliberadamente estrecho: solo la identidad que el libro declara.
"""),
    ]),
    ("05_contrato_e_integracion.ipynb", [
        ("md", """# Contrato e integración de RB-IA-2191

**Dataset:** RB-IA-2191 · **Cuaderno:** 05 · **Tema:** manifiestos, pozos y límites

## Introducción

Para que DATA, PROCESO y VISUALIZACIÓN reconozcan el expediente hacen falta `integracion/pozos.json`, `controles.json`, contratos y motor. Este cuaderno comprueba esos artefactos y recuerda qué no está aprobado.

## Objetivos

Verificar que el pozo declarado es único, que los controles son BFPD/BWPD, y que no hay reglas de caudal.

## Metodología

Se leen los JSON de integración y se contrastan con el día de referencia del libro.
"""),
        ("code", PREAMBULO + """
import json
from pathlib import Path
from rbia2191_lectura import dia_referencia
raiz = Path.cwd()
pozos = json.loads((raiz / "integracion" / "pozos.json").read_text(encoding="utf-8"))
controles = json.loads((raiz / "integracion" / "controles.json").read_text(encoding="utf-8"))
manifiesto = json.loads((raiz / "integracion" / "manifiesto.json").read_text(encoding="utf-8"))
reglas = json.loads((raiz / "integracion" / "reglas.json").read_text(encoding="utf-8"))
ref = dia_referencia()
print("pozos", [p["pozo_rotulo"] for p in pozos["pozos"]])
print("controles", [c["id"] for c in controles["controles"]])
print("reglas", reglas["reglas"])
print("sha manifiesto", manifiesto["sha256_entrada"])
print("ref BFPD/BWPD", ref["BFPD"], ref["BWPD"])
assert pozos["pozos"][0]["condiciones_registradas"]["bfpd"] == ref["BFPD"]
assert manifiesto["estado_reglas"] == "sin_regla_de_caudal"
"""),
        ("md", """## Resultados

Un solo pozo `RB-IA-2191`. Controles `bfpd` y `bwpd`. Lista de reglas vacía. El SHA del manifiesto coincide con el de la copia de trabajo. Las condiciones registradas del pozo reproducen el día de referencia.

## Alcance y restricciones

No hay curva de bomba, ni RC-BES, ni aprobación operacional. El rótulo esperado en consola es REGISTRO (`resultados_sin_regla`). Columnas como Sum, P_SUT o Eff_b permanecen fuera del motor hasta que exista una expresión verificable.

## Conclusión

El expediente queda integrable en HUC con el mismo patrón contractual que RB-1521, pero con su propia identidad matemática.
"""),
    ]),
]


if __name__ == "__main__":
    rutas = construir()
    ejecutar(rutas)
    exportar(rutas)
    print("cuadernos", len(rutas))
    for ruta in rutas:
        pdf = PDFS / f"{ruta.stem}.pdf"
        print(ruta.name, "pdf_bytes", pdf.stat().st_size if pdf.is_file() else 0)
