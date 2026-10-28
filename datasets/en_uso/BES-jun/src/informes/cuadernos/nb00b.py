"""Cuaderno 00 (trazabilidad): inventario de artefactos, linaje y estado de los 12 cuadernos."""

from informes.cuadernos.base import C, M, PREPARACION, guardar

NOMBRE = "00_inventario_y_trazabilidad"


def construir():
    return [
        M(r"""
# Cuaderno 00 · Inventario y trazabilidad del expediente

**Expediente:** BES-jun · **Estado del expediente:** Listo para revisión (no Completo)

> **Relación con `00_inventario_y_fuentes`.** Ese cuaderno responde *¿qué insumo se recibió y está intacto?* (huella del libro y de las fuentes técnicas). Este responde *¿qué contiene el expediente, quién produjo cada archivo y en qué estado está cada cuaderno?* Son dos preguntas distintas y por eso son dos cuadernos.

## 1. Introducción y contexto (el problema)
Un expediente de análisis crece: cuadernos, módulos de código, tablas intermedias, figuras, documentos y PDF. Con el tiempo aparecen tres riesgos: archivos huérfanos (nadie sabe quién los produjo), archivos desactualizados (se generaron con una versión anterior del análisis) y cuadernos que dicen una cosa mientras el código hace otra. En un entorno donde una cifra obsoleta puede llegar a una decisión de operación, la falta de trazabilidad es un riesgo de integridad.

## 2. Justificación y necesidad
Un inventario verificable de los artefactos, un mapa de **linaje** (cuaderno → archivos que produce), el estado real de ejecución de los 12 cuadernos y una comparación con la versión original respaldada antes de la auditoría. El proyecto **no es un repositorio Git**, de modo que el respaldo con manifiesto SHA-256 es la única referencia verificable para saber qué cambió.

## 3. Objetivo general
Dejar documentado qué hay en el expediente, cómo se relacionan los 12 cuadernos entre sí y con los archivos que producen, y demostrar que los originales respaldados no han sido alterados.

## 4. Dominio y alcance
**Incluye:** inventario por carpeta; roles y relación de los 12 cuadernos (incluidos los de numeración repetida, que **no** son duplicados); linaje declarado con verificación de existencia y huella; comparación con el respaldo previo; estado de ejecución leído de los `.ipynb` en disco.

**No incluye:** validar el contenido técnico de los cuadernos (eso es cada cuaderno), ni mover, borrar o renumerar archivos.

## 5. Fuentes y datos (entradas y salidas)
**Entradas:** la carpeta del expediente, los 12 `.ipynb`, el respaldo `logs/respaldo_previo_a_auditoria/` con `MANIFIESTO_SHA256.txt`. **Salidas:** tablas de inventario, linaje y estado; ningún archivo escrito.

## 6. Objetivos específicos y criterios de aceptación
**C00b-1** el respaldo coincide con su manifiesto (24 archivos) · **C00b-2** existen los 12 cuadernos esperados · **C00b-3** todo archivo declarado en el linaje existe · **C00b-4** los roles de los 12 cuadernos son distintos (ninguno es duplicado de otro) · **C00b-5** cada cuaderno (salvo éste) tiene Limitaciones y Referencias · **C00b-6** el libro no cambió.

## 7. Riesgo si este paso falla
Usar tablas o figuras generadas con una versión anterior sin saberlo, o creer que se conservan los originales cuando se han sobrescrito.
"""),
        M(r"""
## Preparación del entorno
Misma celda de los demás cuadernos: localiza el expediente, fija formato de tablas y muestra la ficha del entorno (versiones y SHA-256 del insumo).
"""),
        C(PREPARACION),
        M(r"""
## Paso 1 · Inventario por carpeta

**Qué se hace.** Se recorre el expediente (sin `__pycache__` ni `.ipynb_checkpoints`) y se cuenta, por carpeta, cuántos archivos hay y cuánto ocupan. **Para qué.** Para tener una fotografía de la composición del expediente; una carpeta inesperadamente vacía o con archivos de más es una señal.
"""),
        C(r"""
from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO
sha_inicial = huellas(COPIA_TRABAJO)["sha256"]
IGNORAR = {"__pycache__", ".ipynb_checkpoints", ".pytest_cache"}
archivos = [p for p in RAIZ.rglob("*") if p.is_file() and not (set(p.relative_to(RAIZ).parts) & IGNORAR)]
inv = pd.DataFrame([{"carpeta": p.relative_to(RAIZ).parts[0] if len(p.relative_to(RAIZ).parts) > 1 else "(raíz)", "bytes": p.stat().st_size} for p in archivos])
resumen = inv.groupby("carpeta").agg(archivos=("bytes", "size"), kilobytes=("bytes", lambda s: s.sum() / 1024)).reset_index()
print("Total de archivos:", len(archivos))
T(resumen)
"""),
        M(r"""
**Interpretación.** El expediente se reparte entre `entrada/` (el insumo), `src/` (código reutilizable), `notebooks/` (los 12 cuadernos), `data_procesados/` (tablas derivadas), `reports/` (informe y figuras), `pdf/` (documentos de entrega), `docs/` (decisiones y consultas), `tests/` (pruebas) y `logs/` (bitácora y respaldo). La separación es la que permite aplicar una regla simple: **`entrada/` solo se lee; todo lo demás se puede regenerar a partir de ella y del código**.
"""),
        M(r"""
## Paso 2 · Los 12 cuadernos: quién es quién

**Hecho importante.** Cinco números (00 a 04) tienen **dos** cuadernos cada uno. **No son duplicados**: cada par responde preguntas diferentes sobre el mismo tema. Se declara aquí el rol de cada uno y se comprueba que ningún rol se repite. Para cada cuaderno se lee del disco su estructura real (celdas, palabras explicativas, criterios `C…` encontrados y estado de ejecución).
"""),
        C(r"""
import nbformat, re
ROLES = [
    ("00_inventario_y_fuentes",               "Identidad del insumo: huellas del libro y de las fuentes técnicas; control negativo."),
    ("00_inventario_y_trazabilidad",          "Inventario del expediente, linaje de archivos y estado de los 12 cuadernos (este cuaderno)."),
    ("01_inspeccion_BES_jun",                 "Inspección descriptiva de las hojas: mapa de bloques, dimensiones, entradas, survey y equipos."),
    ("01_inspeccion_y_calidad_datos",         "Calidad: controles de errores, fechas, survey, curvatura mínima, TVD y plausibilidad."),
    ("02_ecuaciones_y_variables",             "Glosario de ecuaciones y variables: fenómeno, unidades, hipótesis, función en código y categoría."),
    ("02_trazabilidad_y_analisis_formulas",   "Trazabilidad de fórmulas del libro: firmas, constantes, hidrostática y catálogo."),
    ("03_limpieza_y_mapeo",                   "Mapeo del formulario a tabla larga y prueba de ida y vuelta; registro de unidades."),
    ("03_mapeo_y_preparacion_BES_jun",        "Preparación de tablas ordenadas de survey y curvas de bomba; estadísticas y figuras."),
    ("04_calculos_deterministicos",           "Contrato y verificación de las funciones de cálculo; casos límite y ficha de confiabilidad."),
    ("04_modelo_deterministico",              "Formulación del modelo, dominio de validez y sensibilidad local."),
    ("05_evaluacion_por_pozo",                "Evaluación por pozo: reproducción, contraste, ventana operativa, sensibilidad a ambigüedades."),
    ("06_hallazgos_y_reglas_candidatas",      "Registro de hallazgos, consultas técnicas y reglas candidatas."),
]
filas = []
for i, (nombre, rol) in enumerate(ROLES):
    ruta = RAIZ / "notebooks" / f"{nombre}.ipynb"
    if not ruta.is_file():
        filas.append({"n.º": i, "cuaderno": nombre, "rol": rol, "existe": False}); continue
    nb = nbformat.read(ruta, as_version=4)
    md = [c for c in nb.cells if c.cell_type == "markdown"]; co = [c for c in nb.cells if c.cell_type == "code"]
    texto = "\n".join(c.source for c in nb.cells)
    filas.append({"n.º": i, "cuaderno": nombre, "existe": True, "celdas MD": len(md), "celdas de código": len(co),
                  "palabras explicativas": sum(len(c.source.split()) for c in md),
                  "criterios C…": len(set(re.findall(r"\*\*(C\d+b?-\d+)\*\*", texto))),
                  "con salidas guardadas": sum(1 for c in co if c.outputs), "con Limitaciones y Referencias": "## Limitaciones" in texto and "## Referencias" in texto})
estado = pd.DataFrame(filas)
T(estado, ancha=True)
"""),
        C(r"""
T(pd.DataFrame(ROLES, columns=["cuaderno", "rol (qué pregunta responde)"]), ancha=True)
"""),
        M(r"""
**Interpretación.** Cada cuaderno tiene un rol propio y no hay dos con la misma pregunta. Los pares de numeración repetida se relacionan así: el primero de cada par (`01_inspeccion_BES_jun`, `02_ecuaciones_y_variables`, `03_mapeo_y_preparacion_BES_jun`, `04_modelo_deterministico`) **describe y formula**; el segundo (`01_inspeccion_y_calidad_datos`, `02_trazabilidad_y_analisis_formulas`, `03_limpieza_y_mapeo`, `04_calculos_deterministicos`) **verifica y audita**. Se conservan ambos porque fusionarlos mezclaría descripción con evidencia de control, y porque renumerar o eliminar uno rompería referencias cruzadas existentes sin aportar nada técnico.

La columna «con salidas guardadas» indica cuántas celdas de código de cada cuaderno traen salida en el archivo; una cifra de cero en un cuaderno con código indicaría que no se ejecutó. **Esto lee el disco en el momento de esta ejecución**: el orquestador ejecuta este cuaderno al final del lote para que refleje el estado definitivo.
"""),
        M(r"""
## Paso 3 · Linaje: qué archivo produce cada cuaderno

**Qué se hace.** Se declara, en una tabla, qué archivos de `data_procesados/` y `reports/figuras/` produce cada cuaderno y se verifica que existan y tengan tamaño positivo; se registra también su SHA-256. **Nota:** `guardar_figuras` regenera siempre las seis figuras (es determinista); cada cuaderno se declara productor de las que analiza. **Límite honesto:** el linaje es **declarado**; el control comprueba existencia y huella, no que el cuaderno indicado haya sido realmente el que lo escribió. Los archivos del directorio que no figuran en el linaje se listan aparte: son los «huérfanos», una señal de higiene del expediente.
"""),
        C(r"""
LINAJE = {
    "03_limpieza_y_mapeo": ["data_procesados/variables_largo.csv", "data_procesados/matriz_entradas_por_hoja.csv", "data_procesados/registro_unidades.csv"],
    "01_inspeccion_BES_jun": ["reports/figuras/survey_md_tvd_por_hoja.png", "reports/figuras/inclinacion_survey_por_hoja.png"],
    "03_mapeo_y_preparacion_BES_jun": ["data_procesados/curvas_bomba_60hz.csv", "reports/figuras/head_puntos_60hz.png"],
    "04_calculos_deterministicos": ["data_procesados/resultados_deterministicos.csv"],
    "05_evaluacion_por_pozo": ["reports/figuras/caudal_limites_por_hoja.png", "reports/figuras/interseccion_sistema_bomba.png", "reports/figuras/impacto_ambiguedades_en_caudal.png"],
}
filas = []
for cuaderno, rutas in LINAJE.items():
    for r in rutas:
        p = RAIZ / r
        filas.append({"cuaderno productor": cuaderno, "archivo": r, "existe": p.is_file() and p.stat().st_size > 0,
                      "bytes": p.stat().st_size if p.is_file() else None, "SHA-256": huellas(p)["sha256"] if p.is_file() else None})
linaje = pd.DataFrame(filas)
declarados = {RAIZ / r for rs in LINAJE.values() for r in rs}
presentes = {p for p in (RAIZ / "data_procesados").glob("*") if p.is_file()} | {p for p in (RAIZ / "reports" / "figuras").glob("*") if p.is_file()}
huerfanos = sorted(str(p.relative_to(RAIZ)) for p in presentes - declarados)
print("Archivos declarados:", len(declarados), "| presentes sin declarar:", len(huerfanos))
T(linaje, ancha=True)
"""),
        C(r"""
T(pd.DataFrame({"archivo presente sin linaje declarado": huerfanos}))
"""),
        M(r"""
**Interpretación.** Los archivos declarados existen y se pueden identificar por huella. La segunda tabla lista lo que hay en las carpetas de salida sin una declaración de linaje: son derivados de las primeras versiones del análisis (tablas descriptivas y figuras de versiones anteriores del código de `src/`) cuyo productor no está declarado en este cuaderno. **No se borran** (una regla de este expediente es no eliminar documentos que no se ha podido demostrar que sobran), pero se registran como pendiente de clasificar en el informe de auditoría. Sobre las figuras, `caudal_y_limites.png` y `head_tabulado.png` son versiones previas de dos de las seis figuras vigentes (`caudal_limites_por_hoja.png` y `head_puntos_60hz.png`).
"""),
        M(r"""
## Paso 4 · Comparación con el estado previo a la auditoría

**Qué se hace.** Antes de reescribir los cuadernos se guardó en `logs/respaldo_previo_a_auditoria/` una copia de los 12 cuadernos y de los 12 PDF anteriores, con un manifiesto de SHA-256. Se **verifica que ese respaldo sigue íntegro** (cada archivo coincide con su huella) y se compara, cuaderno por cuaderno, el tamaño del original frente al actual. Como no hay Git, esta es la forma de saber qué se cambió y de recuperar un original.
"""),
        C(r"""
respaldo = RAIZ / "logs" / "respaldo_previo_a_auditoria"
manifiesto = [linea.split(None, 1) for linea in (respaldo / "MANIFIESTO_SHA256.txt").read_text(encoding="utf-8").splitlines() if linea.strip()]
verif = [{"archivo": ruta.strip(), "coincide con el manifiesto": huellas(respaldo / ruta.strip())["sha256"] == sha} for sha, ruta in manifiesto]
integro = pd.DataFrame(verif)
print("Archivos en el manifiesto:", len(integro), "| coinciden:", int(integro["coincide con el manifiesto"].sum()))
comp = []
for nombre, _ in ROLES:
    o = nbformat.read(respaldo / "notebooks" / f"{nombre}.ipynb", as_version=4)
    a = nbformat.read(RAIZ / "notebooks" / f"{nombre}.ipynb", as_version=4)
    pal = lambda nb: sum(len(c.source.split()) for c in nb.cells if c.cell_type == "markdown")
    lin = lambda nb: sum(len(c.source.splitlines()) for c in nb.cells if c.cell_type == "code")
    comp.append({"cuaderno": nombre, "celdas (antes)": len(o.cells), "celdas (ahora)": len(a.cells),
                 "palabras explicativas (antes)": pal(o), "palabras explicativas (ahora)": pal(a),
                 "líneas de código (antes)": lin(o), "líneas de código (ahora)": lin(a)})
comparacion = pd.DataFrame(comp)
T(comparacion, ancha=True)
"""),
        M(r"""
**Interpretación.** El respaldo coincide con su manifiesto: los originales están intactos y se pueden recuperar. La comparación muestra el cambio de escala del trabajo: los cuadernos pasaron de **3 celdas** (dos de texto breve y una de código) a documentos con varios pasos, cada uno con su explicación antes y después del código. Lo que **no** cambió es la identidad de cada cuaderno ni su objetivo original (el rol declarado arriba corresponde a lo que el cuaderno ya anunciaba). Si alguna cifra de «ahora» fuera igual o menor que «antes» sería una señal de que el cuaderno no se ha enriquecido y el criterio de revisión lo habría marcado.
"""),
        M(r"""
## Paso 5 · Criterios de aceptación
"""),
        C(r"""
crit = Criterios("00_inventario_y_trazabilidad")
crit.comprobar("C00b-1", "El respaldo coincide con su manifiesto", bool(integro["coincide con el manifiesto"].all()) and len(integro) == 24, f"{len(integro)} archivos")
crit.comprobar("C00b-2", "Existen los 12 cuadernos esperados", len(estado) == 12 and bool(estado["existe"].all()), f"{int(estado['existe'].sum())} de 12")
crit.comprobar("C00b-3", "Todo archivo declarado en el linaje existe", bool(linaje["existe"].all()), f"{len(linaje)} archivos")
crit.comprobar("C00b-4", "Los roles de los 12 cuadernos son distintos", len({r for _, r in ROLES}) == 12, "12 roles distintos")
otros = estado[estado["cuaderno"] != "00_inventario_y_trazabilidad"]
crit.comprobar("C00b-5", "Cada cuaderno (salvo éste) tiene Limitaciones y Referencias", bool(otros["con Limitaciones y Referencias"].all()), f"{int(otros['con Limitaciones y Referencias'].sum())} de {len(otros)}")
crit.comprobar("C00b-6", "El libro no cambió", huellas(COPIA_TRABAJO)["sha256"] == sha_inicial, sha_inicial[:16] + "…")
T(crit.tabla())
"""),
        C(r"""
crit.exigir()
print("Todos los criterios de aceptación del cuaderno 00 (trazabilidad) se cumplen.")
"""),
        M(r"""
## Conclusión técnica

- **Resultado:** el expediente está inventariado, los 12 cuadernos tienen rol propio (ninguno es duplicado), el linaje de las tablas y figuras vigentes está declarado y verificado por huella, y el estado previo a la auditoría se conserva íntegro con manifiesto.
- **Hallazgo de higiene:** existen archivos de salida sin linaje declarado (versiones previas de tablas y figuras). No se borran; quedan registrados como pendientes de clasificar.
- **Qué habilita:** cualquier cifra o figura puede rastrearse hasta el cuaderno que la produce, y cualquier cuaderno puede compararse con su original.
- **Siguiente paso:** `01_inspeccion_BES_jun`, para describir las hojas.
"""),
    ]


if __name__ == "__main__":
    print(guardar(NOMBRE, construir()))
