"""Construye, ejecuta y exporta los cuadernos de RB-1521. No toca BES-jun."""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

RAIZ = Path(__file__).resolve().parents[1]
NOTEBOOKS = RAIZ / "notebooks"
PDFS = RAIZ / "pdf" / "notebooks"


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
        html = html_de_cuaderno(ruta).replace("BES-jun · Listo para revisión", "RB-1521 · Serie diaria")
        destino_html = PDFS / f"{ruta.stem}.html"
        destino_pdf = PDFS / f"{ruta.stem}.pdf"
        destino_html.write_text(html, encoding="utf-8")
        pdf_desde_html(destino_html, destino_pdf)


PREAMBULO = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))
"""

CUADERNOS = [
    ("00_inventario_y_fuentes.ipynb", [
        ("md", """# Inventario y fuentes de RB-1521

**Dataset:** RB-1521 · **Expediente:** `datasets/en_uso/RB-1521` · **Cuaderno:** 00 · **Tema:** procedencia del libro

## Introducción

RB-1521 es el dataset D1 del tablero de asesor-esp. Hasta esta investigación el expediente estaba en `en_espera`, con `entrada/` vacía, y la aplicación no abría el `.xls`. El archivo que sí existía era la copia íntegra en `fuentes/originales/` y otra copia suelta en la raíz del proyecto. Este cuaderno fija cuál de esas copias es la fuente, comprueba que la copia de trabajo no se apartó del original y deja el inventario que los cuadernos siguientes van a usar.

## Objetivos

El objetivo general es establecer la identidad del archivo antes de interpretar ninguna columna. Los objetivos específicos son calcular el SHA-256 de la copia de trabajo y del original, comprobar que los bytes coinciden, y registrar el tamaño y el formato sin reescribir el libro.

## Metodología

La comparación es binaria. No se abre el libro con una herramienta que recalcule celdas ni se ejecuta VBA. `hashlib.sha256` lee los bytes del archivo. La ruta de trabajo es `entrada/RB-1521-PY-121120.xls`. La ruta de referencia es `fuentes/originales/RB-1521-PY-121120.xls`. Si los hashes difieren, el resto de la investigación no tiene una fuente única y debe detenerse.

## Alcance

Este cuaderno no describe pozos, unidades ni fórmulas. Solo responde si el archivo que va a leerse es el que entregaron los especialistas.
"""),
        ("code", PREAMBULO + """
from rb1521_lectura import HASH_ORIGINAL, huella, ruta_entrada
original = Path.cwd().parents[2] / "fuentes" / "originales" / "RB-1521-PY-121120.xls"
trabajo = ruta_entrada()
print("bytes trabajo", trabajo.stat().st_size)
print("bytes original", original.stat().st_size)
print("sha trabajo", huella(trabajo))
print("sha original", huella(original))
print("coincide con el registro", huella(trabajo) == HASH_ORIGINAL == huella(original))
print("mismos bytes", trabajo.read_bytes() == original.read_bytes())
"""),
        ("md", """## Resultados e interpretación

La copia de trabajo y el original pesan 84480 bytes y comparten el SHA-256 `3c5043da6255c36c2c4270e465b4ee20dd7e6de534e58b8e84b42d350edf8808`. La lectura posterior puede atribuirse a ese archivo. No se modificó el original al copiarlo.

## Conclusión

La fuente queda identificada. El cuaderno siguiente puede abrir la hoja sin ambigüedad de versión.
"""),
    ]),
    ("01_estructura_y_calidad.ipynb", [
        ("md", """# Estructura y calidad de la serie RB-1521

**Dataset:** RB-1521 · **Cuaderno:** 01 · **Tema:** forma de la tabla y continuidad temporal

## Introducción

Un motor determinístico no puede empezar por el nombre del archivo. Hace falta saber cuántas hojas hay, si la tabla es rectangular, si las fechas forman una serie diaria y qué columnas están vacías. BES-jun organiza cada pozo en una hoja de diseño. RB-1521 no tiene esa forma: es una serie temporal. Tratarla como cinco pozos de BES-jun sería un error de lectura, no una diferencia menor.

## Objetivos

Describir la geometría real del libro, comprobar la continuidad de las fechas y separar columnas constantes, columnas variables y celdas vacías.

## Metodología

`xlrd` 1.2 abre el `.xls` y devuelve el valor almacenado. No se pide a Excel que recalcule. Cada celda vacía permanece como ausencia: no se sustituye por cero, porque cero sería una medición. La continuidad se juzga por la diferencia, en días, entre fechas consecutivas.

## Fundamento

Una serie diaria continua permite hablar de un día de referencia y de un día excepcional. Una serie con huecos obligaría a decidir si el hueco es una parada o un registro perdido. Esa decisión no se toma aquí: primero se mide el calendario.
"""),
        ("code", PREAMBULO + """
from collections import Counter
from rb1521_lectura import fecha_iso, leer_serie
serie = leer_serie()
fechas = [fila["Fecha"] for fila in serie]
deltas = Counter((fechas[i] - fechas[i-1]).days for i in range(1, len(fechas)))
print("filas", len(serie))
print("desde", fecha_iso(fechas[0]), "hasta", fecha_iso(fechas[-1]))
print("deltas", dict(deltas))
vacios = {}
constantes = {}
for clave in serie[0]:
    if clave == "Fecha":
        continue
    valores = [fila[clave] for fila in serie]
    vacios[clave] = sum(v is None for v in valores)
    presentes = [v for v in valores if v is not None]
    if presentes and len(set(presentes)) == 1:
        constantes[clave] = presentes[0]
print("vacíos", {k: v for k, v in vacios.items() if v})
print("constantes", constantes)
"""),
        ("md", """## Resultados

Hay una sola hoja, `Hoja1`, con 129 filas de datos y 32 columnas. Las fechas van del 2020-05-02 al 2020-09-07 y el salto entre filas consecutivas es siempre un día. No hay huecos de calendario.

La bomba almacenada es siempre `S11000N`. También permanecen fijos, en todas las filas, P-Yac, Pburbuja, API, T-Yac, GEP-Water, P-cas, Vel-fluidos, T-tub, D-tub, N-sellos, Z-intake, Z-sensor, Z-perf y L-cable. Es configuración repetida, no una medición diaria.

`Nivel-test` es la única columna con celdas vacías: 99 de 129. Esas ausencias no se imputan.

## Interpretación

El libro describe una serie de un solo conjunto de equipos, no un inventario de varios pozos. El nombre `RB-1521` identifica el archivo; el libro no trae otro código de pozo. Las profundidades y la marca de bomba son parámetros de la serie. HZ, caudales, presiones, nivel, BSW, IP, voltaje, amperaje y P-SUT cambian de día.

## Restricción

Que una columna sea constante no demuestra que el valor sea una medición independiente. Solo demuestra que el archivo la repite. La curva de la bomba S11000N no está en el libro.

## Conclusión

La estructura útil es una tabla diaria de 129×32, continua, con un bloque de configuración fijo y una columna de prueba incompleta. El catálogo de variables parte de esa separación.
"""),
    ]),
    ("02_variables_y_unidades.ipynb", [
        ("md", """# Variables y unidades de RB-1521

**Dataset:** RB-1521 · **Cuaderno:** 02 · **Tema:** qué está nombrado en el archivo y qué unidad no está escrita

## Introducción

Los encabezados son nombres de columna, no un diccionario de unidades. Escribir «psi» o «ft» porque el nombre se parece a una presión o a una profundidad sería adelantar una convención que la celda no declara. Al mismo tiempo, el cálculo que sí se puede cerrar —la partición del caudal— necesita saber si BSW está en fracción o en porcentaje. Esa distinción sí se puede resolver con el dominio numérico del propio archivo.

## Objetivos

Inventariar las 32 columnas, marcar cuáles varían, y justificar la unidad de trabajo de Q-fluidos y de BSW sin atribuir unidades al resto.

## Metodología

Se clasifica cada columna como constante o variable a partir del cuaderno anterior. Para BSW se observa el intervalo de los 129 valores. Un porcentaje escrito como 98,5 no cabe en un máximo de 0,9909. Para el caudal se conserva el rótulo BFPD como unidad de trabajo del plan de asesor-esp, y se deja explícito que el encabezado no la imprime.

## Fundamento

La partición \(Q_{agua} = Q_{fluidos}\\times \\mathrm{BSW}\) solo es adimensionalmente coherente si BSW es una fracción. Si BSW fuera un porcentaje, el producto sería cien veces mayor que la columna Q-water. Esa prueba no asigna unidad a P-sensor ni a Z-perf.
"""),
        ("code", PREAMBULO + """
from rb1521_lectura import leer_serie
serie = leer_serie()
bsw = [fila["BSW"] for fila in serie]
print("BSW min", min(bsw), "max", max(bsw))
print("todos entre 0 y 1", all(0 <= v <= 1 for v in bsw))
print("Q-fluidos min", min(f["Q-fluidos"] for f in serie), "max", max(f["Q-fluidos"] for f in serie))
"""),
        ("md", """## Resultados

BSW recorre 0,974 a 0,9909. Todos los valores están entre 0 y 1. La lectura coherente con Q-water es una fracción, no un porcentaje. Q-fluidos recorre 8128 a 9004. En el plan del proyecto esa magnitud se trata como BFPD; el encabezado de la celda no lo dice, y esta investigación usa BFPD solo como unidad de trabajo de la partición.

No se asigna unidad a PWf, Nivel, IP, P-SUT, VOLT, AMPs ni a las profundidades. Esas columnas se conservan como valores almacenados.

## Interpretación

El catálogo que entra al simulador tiene dos entradas: Q-fluidos y BSW. El resto de la fila no se ofrece como mando, porque no hay una expresión verificada que las consuma.

## Conclusión

La unidad de BSW queda apoyada por el dominio numérico. Las demás unidades quedan sin declarar en el archivo y no se inventan para completar un modelo de bomba.
"""),
    ]),
    ("03_identidades_numericas.ipynb", [
        ("md", """# Identidades numéricas almacenadas en RB-1521

**Dataset:** RB-1521 · **Cuaderno:** 03 · **Tema:** qué relaciones cierran con las celdas y cuáles no

## Introducción

El `.xls` guarda valores. `xlrd` no entrega una fórmula en estas celdas: entrega el número que Excel dejó escrito. Una identidad útil para HUC es una relación que reproduce esas cifras. Una relación que solo se parece en un día no se implementa.

Se contrastan tres candidatas que el nombre de las columnas sugiere, sin traer ecuaciones de BES-jun:

1. \(Q_{agua} = Q_{fluidos}\\times \\mathrm{BSW}\) y \(Q_{petroleo} = Q_{fluidos} - Q_{agua}\).
2. \(\\mathrm{IP} = Q_{fluidos} / (P_{yac} - \\mathrm{PWf})\).
3. \(P_{SUT} = \\sqrt{3}\\, V\\, I\\, \\mathrm{FP} / 1000\) con factores de potencia 0,80, 0,85, 0,90 y 1.

## Objetivos

Contar en cuántas filas cada candidata reproduce el archivo, y conservar solo la que cierra dentro de una tolerancia de \(10^{-9}\).

## Metodología

La tolerancia absoluta de \(10^{-9}\) separa el redondeo binario de una discrepancia de caudal. No se ajustan coeficientes para reducir el error. Si la diferencia máxima es de decenas o cientos, la candidata se rechaza.
"""),
        ("code", PREAMBULO + """
from rb1521_lectura import fecha_iso, leer_serie
from rb1521_particion import identidad_exacta, particionar
serie = leer_serie()
print("filas", len(serie), "partición exacta", sum(identidad_exacta(f) for f in serie))
for fila in serie:
    if not identidad_exacta(fila):
        agua, pet = particionar(fila["Q-fluidos"], fila["BSW"])
        print("excepción", fecha_iso(fila["Fecha"]), "Qw archivo", fila["Q-water"], "Qw producto", agua)
errores_ip = []
for fila in serie:
    denominador = fila["P-Yac"] - fila["PWf"]
    errores_ip.append(abs(fila["IP"] - fila["Q-fluidos"] / denominador))
print("error máximo IP", max(errores_ip))
for fp in (0.8, 0.85, 0.9, 1.0):
    err = max(abs(f["P-SUT"] - (3 ** 0.5) * f["VOLT"] * f["AMPs"] * fp / 1000) for f in serie)
    print("error máximo P-SUT con FP", fp, err)
"""),
        ("md", """## Resultados

La partición de caudal reproduce Q-water y Q-oil en 128 de 129 filas. La única excepción es el 2020-07-09: el archivo guarda Q-water = 8522,984 y el producto \(8841 \\times 0{,}986\) es 8717,226. No se corrige la celda.

El índice de productividad definido como caudal dividido por el contraste de presiones no reproduce IP. El error máximo supera 1 unidad de la columna. La potencia trifásica con los cuatro factores de potencia ensayados deja errores de decenas en P-SUT. Esas dos expresiones no entran al motor.

## Interpretación

HUC puede repartir un caudal y un BSW con la misma relación que el archivo usa en casi toda la serie. No puede, con este libro, reconstruir IP ni P-SUT. Tampoco hay en el archivo una curva de head de la S11000N contra la cual clasificar el punto como se clasifica un pozo de BES-jun.

## Conclusión

El cálculo reproducible es la partición. El día 2020-07-09 queda como discrepancia registrada, no como un valor a forzar.
"""),
    ]),
    ("04_particion_de_caudal.ipynb", [
        ("md", """# Implementación de la partición de caudal

**Dataset:** RB-1521 · **Cuaderno:** 04 · **Tema:** función determinística y día de referencia

## Introducción

La identidad del cuaderno anterior se escribe una vez, en `rb1521_particion.particionar`, y el motor la llama. El día de referencia es la primera fila, 2020-05-02, porque es el inicio de la serie continua y en esa fila la partición cierra. No es un día elegido por ser el más favorable entre varios candidatos: es el origen temporal del archivo.

## Objetivos

Reproducir Q-water y Q-oil del 2020-05-02, y mostrar que un caudal distinto del almacenado produce otro reparto sin escribir el Excel.

## Metodología

El motor lee la copia de trabajo, comprueba el hash y aplica la partición a las entradas recibidas. Si no llegan entradas, usa Q-fluidos y BSW de la primera fila. `recomendacion_operacional_autorizada` permanece en falso: el reparto no es una consigna de maniobra.

## Ecuación

\\[
Q_{agua} = Q_{fluidos} \\times \\mathrm{BSW}, \\qquad Q_{petroleo} = Q_{fluidos} - Q_{agua}
\\]

\(Q_{fluidos}\) es el valor de la columna o el valor sustituido en el escenario. BSW es la fracción de la columna o la sustituida. El resultado se compara con la fila solo cuando las entradas son las de esa fila.
"""),
        ("code", PREAMBULO + """
from evaluacion.motor import evaluar_solicitud
base = evaluar_solicitud({"dataset_id": "RB-1521", "pozo_id": "RB-1521", "variables": []})
esc = evaluar_solicitud({
    "dataset_id": "RB-1521",
    "pozo_id": "RB-1521",
    "variables": [{"nombre": "caudal_fluidos", "valor": 8500, "unidad": "BFPD"}],
})
print("referencia", base["fecha_referencia"], base["modelos"][0]["valores"])
print("coincide con la fila", base["coincidencia_dia_referencia"])
print("escenario 8500", esc["modelos"][0]["valores"]["q_water"], esc["modelos"][0]["valores"]["q_oil"])
print("el escenario ya no es la fila", esc["coincidencia_dia_referencia"])
"""),
        ("md", """## Resultados

El 2020-05-02 el motor devuelve Q-water = 8842,345 y Q-oil = 134,655, que son las cifras almacenadas. Con Q-fluidos = 8500 y el BSW de referencia 0,985, Q-water pasa a 8372,5. La copia del Excel no cambia: la función no tiene una ruta de escritura.

El motor rechaza un pozo de BES-jun y rechaza la frecuencia como entrada, porque la frecuencia no interviene en la partición.

## Interpretación

El simulador puede mover Q-fluidos y BSW dentro de los extremos observados en las 129 filas. Esos extremos describen la serie; no son un límite de bomba. Cambiar la frecuencia no tiene un efecto calculable con las fórmulas que este archivo permite verificar.

## Conclusión

La implementación queda limitada a la partición, con trazabilidad al día de referencia y sin escritura del original.
"""),
    ]),
    ("05_contrato_e_integracion.ipynb", [
        ("md", """# Contrato e integración de RB-1521 en HUC

**Dataset:** RB-1521 · **Cuaderno:** 05 · **Tema:** qué puede publicar el expediente y qué no hereda de BES-jun

## Introducción

BES-jun publica PIP, THD y un caudal de intersección, y enciende el semáforo con reglas de caudal escrito. RB-1521 no tiene esas columnas ni esa curva. Integrarlo copiando la pantalla de BES-jun mostraría presiones que el libro no calcula. El contrato de este expediente publica el reparto de caudal y deja el semáforo sin una clase operacional.

## Objetivos

Fijar el identificador, las salidas y la condición de la lámpara, y comprobar que un pozo de BES-jun no puede entrar a este motor.

## Metodología

La solicitud lleva `dataset_id` y `pozo_id`. El identificador de la serie es `RB-1521` porque el archivo no trae otro. El adaptador de HUC carga `src/evaluacion/motor.py` por ruta de archivo, con un nombre de módulo distinto del motor de BES-jun, para que los dos expedientes no compartan el import `evaluacion.motor`.

## Salidas

El modelo `M-RB1521-PARTICION` devuelve Q-fluidos, BSW, Q-water, Q-oil, el número de días de la serie y el número de días en que la partición cierra. No devuelve PIP ni THD. `recomendacion_operacional_autorizada` es falso. La clasificación de la consola queda en `REGISTRO`: hay un resultado y no hay una regla de caudal que lo pinte de verde, ámbar o rojo.
"""),
        ("code", PREAMBULO + """
from evaluacion.motor import evaluar_solicitud
salida = evaluar_solicitud({"dataset_id": "RB-1521", "pozo_id": "RB-1521"})
valores = salida["modelos"][0]["valores"]
print(sorted(valores))
print("autorizada", salida["recomendacion_operacional_autorizada"])
print("sin regla", salida["resultados_sin_regla"])
print("pozo ajeno", evaluar_solicitud({"pozo_id": "QF-084"})["estado_evaluacion"])
"""),
        ("md", """## Resultados

Las claves publicadas son las seis de la partición y del conteo. No aparece `pip_ft`. Un identificador QF-084 termina en `entrada_invalida`. La serie y el pozo de BES-jun siguen en su propio motor.

## Restricciones que quedan abiertas

No hay curva H-Q de la S11000N en el libro, así que no hay ventana de operación que trasladar al semáforo. IP y P-SUT no reproducen las expresiones ensayadas. P-14, la pregunta sobre el lugar de BES-jun frente a este D1 en el tablero de asesor-esp, sigue sin respuesta y no se cierra en este cuaderno. El expediente no pasa a `procesadas`.

## Conclusión

RB-1521 queda integrable como serie de un conjunto de equipos, con un cálculo de partición verificable y sin un modelo de bomba. El visualizador debe mostrar esas salidas y no las de BES-jun.
"""),
    ]),
]


if __name__ == "__main__":
    rutas = construir()
    ejecutar(rutas)
    exportar(rutas)
    print("cuadernos", len(rutas))
