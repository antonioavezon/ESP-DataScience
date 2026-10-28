"""Cuaderno 01: inspección de estructura y calidad de datos."""

from informes.cuadernos.base import C, M, PREPARACION, guardar

NOMBRE = "01_inspeccion_y_calidad_datos"


def construir():
    return [
        M(r"""
# Cuaderno 01 · Inspección de estructura y calidad de datos

**Expediente:** BES-jun · **Cuaderno:** 2 de 7 · **Estado del expediente:** Listo para revisión (no Completo)

## 1. Introducción y contexto (el problema)
El libro no es una tabla: es un **formulario de presentación** (celdas combinadas, rótulos y valores mezclados, sin fila de encabezado) con 1 270 fórmulas en cinco hojas. Una lectura por posición fija funciona en una hoja y falla **sin avisar** en otra, porque las filas se desplazan entre hojas. Un valor leído de la celda equivocada es un número plausible pero falso que entra a la cadena de cálculo.

## 2. Justificación y necesidad
Antes de transcribir cualquier fórmula hay que saber: dónde está cada dato en cada hoja, qué defectos trae el libro (errores guardados, fechas que cambian solas, datos faltantes) y si los datos geométricos (survey, profundidades de equipos) son internamente coherentes. Hay que poder decir, con evidencia, qué defectos **sí** afectan a los cálculos y cuáles no.

## 3. Objetivo general
Emitir un dictamen de calidad por hoja, apoyado en controles ejecutables y reproducibles, que distinga defectos que contaminan la cadena de cálculo de defectos que no.

## 4. Dominio y alcance
**Incluye:** inventario estructural; anclaje por rótulo y demostración del riesgo de la coordenada fija; datos faltantes; errores cacheados y rastreo de dependencias; fechas; geometría del survey y contraste con el método de curvatura mínima; coherencia de las TVD de equipos con el survey; controles de dominio sobre las entradas.

**No incluye:** corregir o imputar valores (no se modifica nada); interpretar la física de las fórmulas (cuaderno 02); juzgar si las condiciones de operación son «buenas» o «malas» (no hay límites aprobados).

## 5. Fuentes y datos (entradas y salidas)
**Entradas:** `entrada/BES_jun.xlsx` (copia verificada en el cuaderno 00). **Salidas:** tablas de inventario, anclas, errores, precedentes, survey, TVD y plausibilidad; dictamen por hoja.

## 6. Objetivos específicos y criterios de aceptación
**C01-1** 5 hojas visibles y 1 270 fórmulas inventariadas · **C01-2** todos los rótulos clave hallados en todas las hojas · **C01-3** ningún error guardado es precedente de THD ni de «Caudal a producir» · **C01-4** cero datos requeridos faltantes · **C01-5** geometría del survey correcta en las 5 hojas · **C01-6** survey = curvatura mínima dentro de 0.01 ft / 0.01 °/100 ft · **C01-7** TVD de equipos = interpolación del survey (< 1e-6 ft) · **C01-8** ningún control de dominio incumplido · **C01-9** el libro no cambió durante el cuaderno.

## 7. Riesgo si este paso falla
Una entrada mal leída o un error guardado que entra a la cadena produce PIP, THD y caudales con apariencia normal. Si además el survey fuera inconsistente, todas las profundidades de equipos —y con ellas la presión en el intake— quedarían sesgadas sin señal visible.
"""),
        M(r"""
## Preparación del entorno
La celda siguiente es la misma en todos los cuadernos: localiza el expediente, habilita `src/` y registra la ficha de reproducibilidad (fecha, versiones y huella del insumo).
"""),
        C(PREPARACION),
        C(r"""
from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO, leer_libro
sha_inicial = huellas(COPIA_TRABAJO)["sha256"]      # se compara de nuevo al final (C01-9)
hojas = leer_libro()                                # lectura sin guardar; abre el libro 2 veces (fórmulas y caché)
print("Hojas leídas:", [h["hoja"] for h in hojas])
"""),
        M(r"""
## Paso 1 · Inventario estructural

**Qué se hace.** Se recorre cada celda y se clasifica como fórmula, constante o error guardado; se cuentan celdas combinadas y se listan las funciones de Excel usadas. **Por qué.** Sirve para dimensionar el problema: un libro con 1 270 fórmulas y casi 5 000 constantes no puede revisarse a ojo. También responde una pregunta de aislamiento: si alguna fórmula citara **otra hoja**, un cambio en una hoja contaminaría a otra y no podríamos tratarlas por separado.
"""),
        C(r"""
from ingesta.estructura_libro import inventario_hojas
inv = pd.DataFrame(inventario_hojas())
inv["usa TODAY()"] = inv["funciones"].str.contains("TODAY")
print("Fórmulas totales:", int(inv["formulas"].sum()), "| constantes totales:", int(inv["constantes"].sum()),
      "| fórmulas que citan otra hoja:", int(inv["formulas_que_citan_otra_hoja"].sum()))
T(inv[["hoja", "estado", "dimension", "celdas_combinadas", "formulas", "constantes", "errores_en_cache", "usa TODAY()"]])
"""),
        C(r"""
T(inv[["hoja", "funciones"]])
"""),
        M(r"""
**Interpretación.**
- Las cinco hojas están **visibles** y ninguna fórmula cita otra hoja: cada hoja es un cálculo **autónomo** y puede tratarse por separado sin riesgo de contaminación cruzada. (No implica que sean independientes entre sí en sus datos: comparten tablas de bomba, ver cuaderno 06.)
- Las funciones son pocas y elementales (`INDEX`, `MATCH`, `IF`, `SQRT`, `AVERAGE`, `TODAY`). `MATCH`/`INDEX` implementan las interpolaciones de profundidad y la intersección con la curva de bomba; `TODAY` es la fecha del encabezado.
- Cuatro de las cinco hojas usan `TODAY()`; la restante (QF-549HST) tiene una fecha escrita. Se detalla en el Paso 5.
- `QF-549HST` es la única con errores guardados (13). El Paso 4 demuestra si importan.
"""),
        M(r"""
## Paso 2 · Por qué las celdas se buscan por rótulo y no por coordenada

**Hipótesis a poner a prueba.** Las cinco hojas parecen la misma plantilla, así que sería tentador leer, por ejemplo, el caudal de operación siempre de `B71`. Se contrasta esa idea con los hechos: se busca cada rótulo clave en cada hoja (`anclas_por_hoja`) y después se compara lo que leería la coordenada fija `B71` contra el valor correcto.
"""),
        C(r"""
from ingesta.estructura_libro import anclas_por_hoja
anclas = pd.DataFrame(anclas_por_hoja()).rename(columns={
    "Descarga (mecánica)": "Descarga", "Intake (mecánica)": "Intake", "Sensor (mecánica)": "Sensor",
    "Velocidad (operación)": "Velocidad", "Caudal (operación)": "Caudal", "Presión de Sensor": "P sensor",
    "PIP en (ft)": "PIP ft", "THD TOTAL": "THD", "Limite maximo": "Lím. máx", "Caudal a producir": "Q producir"})
print("Fila donde está cada rótulo en cada hoja:")
T(anclas)
"""),
        C(r"""
from openpyxl import load_workbook
wb = load_workbook(COPIA_TRABAJO, data_only=True)
demo = []
for h in hojas:
    ws = wb[h["hoja"]]
    leido = ws["B71"].value
    demo.append({"hoja": h["hoja"], "rótulo en A71": ws["A71"].value, "valor en B71": leido,
                 "caudal correcto (por rótulo)": h["caudal_operacion_bfpd"],
                 "¿coincide?": leido == h["caudal_operacion_bfpd"]})
wb.close()
print("Lo que habría leído un acceso por coordenada fija B71:")
T(pd.DataFrame(demo))
"""),
        M(r"""
**Interpretación.** Las filas de los bloques **cambian entre hojas** (p. ej. «Caudal a producir» está en las filas 106, 104, 105, 103 y 103). La coordenada fija `B71` solo acierta en la primera hoja; en las otras devolvería el valor de **otra variable** o una celda vacía, y lo haría sin ningún error. Esta es la justificación técnica del diseño del lector: busca por **texto de rótulo**, y si un rótulo no aparece devuelve «faltante» en vez de adivinar. El cuaderno 03 deja registrada, para cada variable, la celda concreta de la que salió.
"""),
        M(r"""
## Paso 3 · Datos requeridos: ¿falta algo?

Un cálculo con una entrada ausente debe **declararse no calculable**, no completarse con un supuesto. Se verifica que las 19 variables que consumen las fórmulas del expediente estén presentes en las cinco hojas, y que la tabla de la bomba tenga puntos.
"""),
        C(r"""
requeridas = ["frecuencia_hz", "caudal_operacion_bfpd", "presion_sensor_psi", "thp_psi", "id_tubing_in", "etapas",
              "api_deg", "bsw_numero", "temperatura_c", "densidad_agua_lb_gal", "tvd_descarga_ft", "tvd_intake_ft",
              "tvd_sensor_ft", "frecuencia_curva_hz", "limite_minimo_bfpd", "limite_maximo_bfpd",
              "cache_pip_ft", "cache_thd_ft", "cache_caudal_producir_bfpd"]
completitud = []
for h in hojas:
    faltan = [k for k in requeridas if h.get(k) is None]
    completitud.append({"hoja": h["hoja"], "requeridas": len(requeridas),
                        "presentes": len(requeridas) - len(faltan),
                        "faltantes": ", ".join(faltan) or "ninguna",
                        "puntos en tabla de bomba": len(h["curva"])})
T(pd.DataFrame(completitud))
"""),
        M(r"""
**Interpretación.** No falta ninguna entrada requerida y las tablas de bomba tienen seis puntos en todas las hojas. Esto **no** significa que los valores sean correctos, solo que existen. La correctitud física se aborda en los Pasos 6 a 8.
"""),
        M(r"""
## Paso 4 · Errores guardados y rastreo de dependencias

**Hecho.** Excel guarda el resultado de cada fórmula; si una fórmula divide por cero, guarda `#DIV/0!`. **Pregunta de ingeniería.** ¿Esos errores contaminan lo que calculamos (PIP, THD, caudal a producir) o están en otra parte de la hoja? Afirmar «no importan» sin demostrarlo sería un riesgo; por eso se **rastrean las precedencias**: a partir de la celda resultado se recorre, fórmula por fórmula, todo de lo que depende (`precedentes`), y se verifica si alguna celda con error aparece en ese conjunto.
"""),
        C(r"""
from ingesta.estructura_libro import errores_cacheados
errores = pd.DataFrame(errores_cacheados())
print("Errores guardados en el libro:", len(errores), "| por hoja:", errores["hoja"].value_counts().to_dict())
T(errores)
"""),
        C(r"""
from analisis.dependencias import precedentes
wf = load_workbook(COPIA_TRABAJO, data_only=False)
con_error = errores.groupby("hoja")["celda"].apply(set).to_dict()
filas = []
for a in anclas_por_hoja():
    ws = wf[a["hoja"]]
    for nombre, celda in (("THD TOTAL", f"G{a['THD TOTAL']}"), ("Caudal a producir", f"B{a['Caudal a producir']}")):
        p = precedentes(ws, celda)
        comunes = (p["formulas"] | p["constantes"]) & con_error.get(a["hoja"], set())
        filas.append({"hoja": a["hoja"], "resultado": nombre, "celda": celda,
                      "fórmulas precedentes": len(p["formulas"]), "constantes precedentes": len(p["constantes"]),
                      "cita otra hoja": p["cita_otra_hoja"], "errores entre precedentes": len(comunes)})
wf.close()
rastreo = pd.DataFrame(filas)
T(rastreo)
"""),
        M(r"""
**Interpretación.** Los 13 errores son `#DIV/0!` y están todos en `QF-549HST`, en la columna D de un bloque lejano a la cadena de cálculo. El rastreo muestra que **ninguna** de las celdas de las que dependen THD y «Caudal a producir» es una celda con error, en ninguna hoja. Por tanto estos errores son un defecto **del libro** (conviene avisarlo a quien lo mantiene) pero **no contaminan** los cálculos de este expediente. La conclusión se limita a eso: no se afirma nada sobre el bloque donde están los errores, que queda fuera del alcance.

*Límite del método:* el rastreo lee referencias `A1` escritas en la fórmula (con rangos); no evalúa funciones ni sigue nombres definidos (el libro no tiene) ni otras hojas (ninguna fórmula las cita, Paso 1).
"""),
        M(r"""
## Paso 5 · Fechas del encabezado

Una fecha en el encabezado de un ensayo de pozo suele indicar **cuándo** se tomó el punto. Aquí hay que comprobar si realmente lo hace, porque de eso depende si se puede ordenar los datos en el tiempo.
"""),
        C(r"""
T(pd.DataFrame([{"hoja": h["hoja"], "fórmula/valor en la celda de fecha": h["fecha_formula"],
                 "valor guardado": h["fecha_cache"], "es TODAY()": h["fecha_es_today"]} for h in hojas]))
"""),
        M(r"""
**Interpretación.** En cuatro hojas la fecha es `=TODAY()`: es la **fecha en que Excel recalculó**, no la fecha del ensayo. Cambia cada día que se abre el libro. En la quinta hoja hay una fecha escrita (2017-09-06) sin que el libro explique a qué corresponde. **Consecuencia:** el libro **no permite análisis temporal** ni ordenar los puntos por fecha. Cada hoja es un punto de operación aislado.
"""),
        M(r"""
## Paso 6 · Coherencia geométrica del survey

El survey (tabla de estaciones MD, inclinación, azimut, TVD y *dogleg*) define las profundidades verticales que usa la hoja para corregir presiones. Si fuera incoherente, el error se propagaría a todo. Se hacen **dos tipos de control**:

1. **Propiedades geométricas** que cualquier survey debe cumplir: MD estrictamente creciente y sin duplicados; TVD ≤ MD; inclinación en [0°, 180°]; azimut en [0°, 360°]; sin nulos.
2. **Contraste independiente.** Se recalculan TVD y *dogleg* con el **método de curvatura mínima**, procedimiento estándar de la industria, y se comparan con las columnas de la hoja. *Importante:* ese método **no es una fórmula de este proyecto**; se usa solo como control externo. La tolerancia es 0.01, una unidad del último decimal que muestra la hoja; no es un límite de ingeniería.
"""),
        C(r"""
from ingesta.survey import leer_survey
from analisis.calidad import verificar_survey, contrastar_con_curvatura_minima
estaciones = leer_survey()
geom, mcm = [], []
for h in hojas:
    est = [e for e in estaciones if e["hoja"] == h["hoja"]]
    geom.append({"hoja": h["hoja"], **verificar_survey(est)})
    mcm.append({"hoja": h["hoja"], **contrastar_con_curvatura_minima(est)})
geom = pd.DataFrame(geom)
mcm = pd.DataFrame(mcm)
T(geom[["hoja", "estaciones", "md_final_ft", "md_estrictamente_creciente", "md_duplicadas",
        "vertical_menor_o_igual_que_md", "vertical_monotona", "inclinacion_max_deg", "azimut_en_0_360", "valores_nulos"]]
  .rename(columns={"md_estrictamente_creciente": "MD creciente", "md_duplicadas": "MD duplic.",
                   "vertical_menor_o_igual_que_md": "TVD≤MD", "vertical_monotona": "TVD monótona",
                   "inclinacion_max_deg": "inc. máx (°)", "azimut_en_0_360": "azim. 0-360", "valores_nulos": "nulos",
                   "md_final_ft": "MD final (ft)"}), ancha=True)
"""),
        C(r"""
T(mcm.rename(columns={"max_dif_tvd_ft": "máx |ΔTVD| (ft)", "max_dif_dogleg_deg_100ft": "máx |Δdogleg| (°/100 ft)",
                      "coincide_dentro_del_redondeo": "coincide"}))
"""),
        M(r"""
**Interpretación.**
- La geometría cumple en las cinco hojas: MD estrictamente creciente, sin duplicados ni nulos, TVD ≤ MD.
- **«TVD monótona = no»** no es un defecto: con inclinaciones por encima de 90° (hasta ≈ 91.5° en algunas hojas) el pozo puede subir ligeramente y la profundidad vertical decrece en tramos. Una regla «TVD siempre creciente» habría dado una **falsa alarma**.
- Las columnas **Vertical** y **Dogleg** de la hoja coinciden con el recálculo por curvatura mínima con diferencias por debajo de 0.005 (el redondeo a dos decimales de la hoja). Esto cierra un pendiente anterior (el método con que se obtuvo `Vertical` no estaba verificado): ahora se sabe que es **coherente con curvatura mínima**.
- *Límite:* es coherencia interna; no demuestra que el survey medido en campo sea exacto.
"""),
        M(r"""
## Paso 7 · ¿De dónde salen las TVD de descarga, intake y sensor?

La hoja escribe MD de cada equipo y calcula la TVD con `MATCH`/`INDEX` sobre el survey. Se **reproduce** esa interpolación en Python (`np.interp`, lineal) y se compara con el valor que guarda la hoja. Además se exige que la MD del equipo esté **dentro del rango del survey** (extrapolar sería un error silencioso) y que TVD ≤ MD.
"""),
        C(r"""
from analisis.calidad import verificar_tvd_de_equipos
tvd_equipos = pd.DataFrame([f for h in hojas for f in verificar_tvd_de_equipos(
    h, [e for e in estaciones if e["hoja"] == h["hoja"]])])
T(tvd_equipos.rename(columns={"md_ft": "MD (ft)", "tvd_hoja_ft": "TVD hoja (ft)", "tvd_interpolada_ft": "TVD interpolada (ft)",
                              "dif_ft": "dif (ft)", "dentro_del_survey": "MD dentro del survey",
                              "tvd_menor_o_igual_que_md": "TVD≤MD"}))
"""),
        M(r"""
**Interpretación.** Las 15 TVD (3 equipos × 5 hojas) coinciden con la interpolación lineal del survey con diferencia nula, todas las MD están dentro del rango y TVD ≤ MD. Por tanto las profundidades que usan PIP, THP y fricción **provienen del survey** y se pueden reproducir de forma independiente. *Límite:* se verifica la interpolación, no que las MD de los equipos sean las reales de la completación.
"""),
        M(r"""
## Paso 8 · Controles de dominio sobre las entradas

Los controles `D-xx` son condiciones **sin las cuales la fórmula transcrita deja de tener sentido** (p. ej. `°API > −131.5` porque la fórmula divide por `131.5 + °API`; `BS&W ∈ [0, 1]` porque la fórmula lo multiplica como fracción). Los `G-xx` son geometría básica de la sarta. El `O-01` es una **observación**, no un juicio: compara la presión del sensor con la de burbuja, porque la cadena de fluido no modela gas libre. **No se importan límites de operación** de otras fuentes: sin ellos no se puede decir que una condición sea «buena» o «mala».
"""),
        C(r"""
from analisis.calidad import plausibilidad_operacion
pl = pd.DataFrame([f for h in hojas for f in plausibilidad_operacion(h)])
orden = [h["hoja"] for h in hojas]
pivote = pl.pivot(index=["control", "descripcion"], columns="hoja", values="resultado")[orden].reset_index()
no_cumple = int((pl["resultado"] == "NO CUMPLE").sum())
print("Controles ejecutados:", len(pl), "| incumplimientos:", no_cumple)
T(pivote, ancha=True)
"""),
        M(r"""
**Interpretación.** No hay incumplimientos. La observación `O-01` indica que la presión del sensor supera la de burbuja en todas las hojas: eso es coherente con una cadena de fluido que **no modela gas libre**, pero es una observación, no una validación de la hipótesis monofásica. Un valor que **sí** hubiera fallado (por ejemplo `BS&W = 97.55`, que es como se leería «%») lo detecta `D-06`; esa detección está cubierta por una prueba automática (`tests/test_controles_y_mapeo.py`).
"""),
        M(r"""
## Paso 9 · Criterios de aceptación y dictamen por hoja
"""),
        C(r"""
crit = Criterios("01_inspeccion_y_calidad_datos")
sha_final = huellas(COPIA_TRABAJO)["sha256"]
crit.comprobar("C01-1", "5 hojas visibles y 1 270 fórmulas inventariadas",
               len(inv) == 5 and (inv["estado"] == "visible").all() and int(inv["formulas"].sum()) == 1270,
               f"hojas={len(inv)}, fórmulas={int(inv['formulas'].sum())}")
crit.comprobar("C01-2", "Rótulos clave hallados en todas las hojas", bool(anclas.drop(columns="hoja").notna().all().all()),
               "sin None en la tabla de anclas")
crit.comprobar("C01-3", "Ningún error guardado es precedente de THD ni de Q a producir",
               int(rastreo["errores entre precedentes"].sum()) == 0 and not rastreo["cita otra hoja"].any(),
               f"{len(errores)} errores; 0 en {len(rastreo)} cadenas rastreadas")
crit.comprobar("C01-4", "Cero datos requeridos faltantes", all(c["faltantes"] == "ninguna" for c in completitud),
               f"{len(requeridas)} variables x {len(hojas)} hojas")
crit.comprobar("C01-5", "Geometría del survey correcta en las 5 hojas",
               bool(geom[["md_estrictamente_creciente", "vertical_menor_o_igual_que_md", "inclinacion_en_0_180", "azimut_en_0_360"]].all().all())
               and int(geom["md_duplicadas"].sum()) == 0 and int(geom["valores_nulos"].sum()) == 0, "5/5 hojas")
crit.comprobar("C01-6", "Survey = curvatura mínima dentro de 0.01", bool(mcm["coincide_dentro_del_redondeo"].all()),
               f"máx ΔTVD={mcm['max_dif_tvd_ft'].max():.4f} ft; máx Δdogleg={mcm['max_dif_dogleg_deg_100ft'].max():.4f}")
crit.comprobar("C01-7", "TVD de equipos = interpolación del survey",
               bool(tvd_equipos["dentro_del_survey"].all()) and bool((tvd_equipos["dif_ft"].abs() < 1e-6).all()) and bool(tvd_equipos["tvd_menor_o_igual_que_md"].all()),
               f"{len(tvd_equipos)} comparaciones")
crit.comprobar("C01-8", "Ningún control de dominio incumplido", no_cumple == 0, f"{len(pl)} controles")
crit.comprobar("C01-9", "El libro no cambió durante el cuaderno", sha_inicial == sha_final, sha_final[:16] + "…")
T(crit.tabla())
"""),
        C(r"""
crit.exigir()
dictamen = []
for h in hojas:
    n = h["hoja"]
    g, m = geom[geom["hoja"] == n].iloc[0], mcm[mcm["hoja"] == n].iloc[0]
    t = tvd_equipos[tvd_equipos["hoja"] == n]
    en_cadena = int(rastreo.loc[rastreo["hoja"] == n, "errores entre precedentes"].sum())
    sin_incumplimientos = not (pl[(pl["hoja"] == n)]["resultado"] == "NO CUMPLE").any()
    apta = (en_cadena == 0 and bool(m["coincide_dentro_del_redondeo"]) and bool(t["dif_ft"].abs().lt(1e-6).all())
            and bool(g["md_estrictamente_creciente"]) and sin_incumplimientos)
    dictamen.append({
        "hoja": n, "pozo": h["pozo"],
        "errores guardados": int((errores["hoja"] == n).sum()),
        "errores en la cadena": en_cadena,
        "survey = curvatura mínima": bool(m["coincide_dentro_del_redondeo"]),
        "TVD de equipos = survey": bool(t["dif_ft"].abs().lt(1e-6).all()),
        "dictamen": "Apta para reproducir el cálculo de la hoja; no para decidir" if apta else "NO APTA: ver controles",
    })
T(pd.DataFrame(dictamen))
"""),
        M(r"""
## Conclusión técnica

- **Resultado:** el libro es estructuralmente sano para el propósito del expediente. Las cinco hojas son cálculos autónomos; los 13 `#DIV/0!` están fuera de la cadena; el survey es coherente con curvatura mínima; las TVD de los equipos provienen del survey.
- **Defectos reales que sí afectan el uso:** (1) las fechas `=TODAY()` impiden análisis temporal; (2) las posiciones cambian entre hojas, así que **toda lectura debe ser por rótulo**; (3) los 13 errores deben comunicarse a quien mantiene el libro.
- **Lo que este cuaderno no puede decir:** que los valores medidos (presiones, caudales) sean correctos; solo que están completos, en dominio y que las profundidades son internamente consistentes.
- **Dictamen:** «apta para reproducir el cálculo de la hoja». La frase **no** equivale a «apta para decidir»: las reservas físicas (BS&W, signo de PIP, constantes) se tratan en los cuadernos 02 a 05.
- **Siguiente paso:** cuaderno 02, trazabilidad de las fórmulas.
"""),
    ]


if __name__ == "__main__":
    print(guardar(NOMBRE, construir()))
