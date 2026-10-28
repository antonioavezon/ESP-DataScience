"""Cuaderno 01 (inspección descriptiva)."""

from informes.cuadernos.base import C, M, PREPARACION, guardar

NOMBRE = "01_inspeccion_BES_jun"


def construir():
    return [
        M(r"""
# Cuaderno 01 · Inspección de las hojas BES-jun

**Expediente:** BES-jun · **Estado del expediente:** Listo para revisión (no Completo)

> **Relación con `01_inspeccion_y_calidad_datos`.** Este cuaderno **describe** el libro (qué hay, dónde, con qué forma). El de calidad **controla** el libro (errores, plausibilidad, curvatura). Primero se mira, después se audita.

## 1. Introducción y contexto (el problema)
El libro `BES_jun.xlsx` es un formulario de cálculo de bombeo electrosumergible (BES) repetido en cinco hojas, una por pozo (`QF-554H`, `QF-545H`, `QF-500H`, `QF-378HST`, `QF-549HST`). No es una base de datos: es una hoja de Excel pensada para que una persona la lea, con celdas combinadas, bloques de texto y fórmulas. Antes de extraer una sola cifra hay que entender cómo está armada, porque **leer la celda equivocada produce un número plausible y falso**.

## 2. Justificación y necesidad
Un mapa verificable de cada hoja: dónde está cada bloque, cuántas fórmulas y constantes contiene, qué datos de operación trae, cómo es el survey (trayectoria) y dónde van los equipos del pozo. Sin ese mapa, cualquier lectura automática descansa en supuestos.

## 3. Objetivo general
Describir con evidencia la estructura y el contenido de las cinco hojas, de modo que las lecturas posteriores (mapeo, cálculos) se apoyen en un conocimiento comprobado del libro.

## 4. Dominio y alcance
**Incluye:** posición de los bloques por rótulo; dimensiones y composición de cada hoja; ficha de operación por pozo; survey (estaciones, profundidad medida, inclinación, desviación); posición de descarga, intake y sensor; dos figuras del survey.

**No incluye:** controles de calidad (cuaderno de calidad), cálculo de PIP/THD, ni conclusiones de operación. Es **descripción**, sin interpretar ningún pozo como «bueno» o «malo».

## 5. Fuentes y datos (entradas y salidas)
**Entrada:** `entrada/BES_jun.xlsx` (solo lectura). **Salidas:** tablas en el cuaderno y dos figuras (`reports/figuras/survey_md_tvd_por_hoja.png` y `inclinacion_survey_por_hoja.png`).

## 6. Objetivos específicos y criterios de aceptación
**C01b-1** las cinco hojas tienen todos los bloques ubicados · **C01b-2** las cinco hojas comparten el mismo número de columnas · **C01b-3** en las cinco hojas la TVD respeta el orden descarga < intake < sensor · **C01b-4** la profundidad medida del survey crece estrictamente en cada hoja · **C01b-5** las dos figuras existen · **C01b-6** el libro no cambió.

## 7. Riesgo si este paso falla
Leer un bloque con coordenadas fijas, o asumir que un dato es de un pozo cuando es de otro. En un formulario donde las filas se desplazan entre hojas, un error de lectura no produce un fallo visible: produce un número equivocado.
"""),
        M(r"""
## Preparación del entorno
"""),
        C(PREPARACION),
        C(r"""
from IPython.display import Image, display
from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO, leer_libro
from ingesta.survey import leer_survey
from ingesta.estructura_libro import anclas_por_hoja, inventario_hojas
from analisis.graficos import guardar_figuras
sha_inicial = huellas(COPIA_TRABAJO)["sha256"]
hojas, estaciones = leer_libro(), leer_survey()
print(len(hojas), "hojas leídas;", len(estaciones), "estaciones de survey")
"""),
        M(r"""
## Paso 1 · Mapa de bloques: dónde está cada cosa

**Qué se hace.** Cada bloque del formulario tiene un **rótulo** en la columna A (por ejemplo «Caudal a producir» o «PIP en (ft)»). Se busca la fila de cada rótulo en cada hoja. **Por qué por rótulo.** Si el formulario fuera idéntico en las cinco hojas, bastaría una coordenada fija; si las filas se desplazan, una coordenada fija leería el dato de otra variable. Lo que sigue lo comprueba.
"""),
        C(r"""
anclas = pd.DataFrame(anclas_por_hoja()).set_index("hoja").T
anclas.index.name = "rótulo"
T(anclas.reset_index(), ancha=True)
"""),
        C(r"""
desplaz = anclas.sub(anclas["QF-554H"], axis=0)
T(desplaz.reset_index().rename(columns=lambda c: f"Δ fila {c}" if c != "rótulo" else c), ancha=True)
print("Rótulos cuya fila cambia en alguna hoja:", int((desplaz != 0).any(axis=1).sum()), "de", len(desplaz))
"""),
        M(r"""
**Interpretación de las dos tablas.** Los diez rótulos cambian de fila en al menos una hoja. Respecto de `QF-554H`, las demás están desplazadas entre **1 y 3 filas**, y el desplazamiento **no es uniforme** ni siquiera dentro de una hoja: en `QF-378HST` el bloque «Descarga (mecánica)» se mueve 1 fila, pero «Velocidad (operación)» se mueve 3. Un ejemplo concreto: «Caudal a producir» está en la fila 106 de `QF-554H`, en la 104 de `QF-545H`, en la 105 de `QF-500H` y en la 103 de `QF-378HST` y `QF-549HST`; estas dos últimas coinciden entre sí en las diez filas, lo que sugiere que comparten plantilla. **Consecuencia:** una lectura con coordenada fija (por ejemplo, tomar siempre la fila 71 para el caudal) leería, en las cuatro hojas desplazadas, el dato de **otra** variable sin ningún aviso. Por eso el código busca por rótulo, y el cuaderno `03_limpieza_y_mapeo` comprueba con una prueba de ida y vuelta que la celda leída es la del rótulo buscado.
"""),
        M(r"""
## Paso 2 · Dimensiones y composición de cada hoja

**Qué se hace.** Se cuentan, por hoja, filas, columnas, celdas combinadas, fórmulas, constantes y funciones de Excel utilizadas. **Para qué.** Una hoja con muchas más fórmulas que las demás, o con una función distinta, sería una versión diferente del cálculo.
"""),
        C(r"""
comp = pd.DataFrame(inventario_hojas())
T(comp[["hoja", "estado", "dimension", "filas", "columnas", "celdas_combinadas", "formulas", "constantes", "formulas_que_citan_otra_hoja", "errores_en_cache"]], ancha=True)
"""),
        C(r"""
T(comp[["hoja", "funciones"]], ancha=True)
"""),
        M(r"""
**Interpretación.** Las cinco hojas ocupan siempre 19 columnas (A:S) y entre 343 y 388 filas; contienen entre 240 y 263 fórmulas y entre 935 y 1031 constantes. **Ninguna fórmula cita otra hoja** (columna `formulas_que_citan_otra_hoja` = 0): las hojas son cálculos **autónomos**, sin vínculos entre sí. Esto es lo que permite tratar cada hoja como un punto de operación independiente y lo que haría un error grave mezclarlas. Las funciones de Excel que aparecen son las mismas (`IF`, `INDEX`, `MATCH`, `SQRT`, `TODAY`, `AVERAGE`), pero no en la misma cantidad: `QF-545H` no usa `AVERAGE`, `QF-549HST` usa 9 en lugar de 18 y 16 `SQRT` en lugar de 19, y esa misma hoja no tiene `TODAY`. Esas diferencias están en bloques secundarios; que las nueve celdas de la cadena de cálculo tienen una **firma estructural idéntica** en las cinco hojas se demuestra en `02_trazabilidad_y_analisis_formulas`. Los 13 errores guardados en caché están todos en `QF-549HST` y se rastrean en el cuaderno de calidad.
"""),
        M(r"""
## Paso 3 · Ficha de operación de cada pozo

**Qué se hace.** Se tabulan, tal como los lee el código por rótulo, los datos de operación y del fluido de cada hoja, con su unidad **rotulada en la hoja**. Es el conjunto de entradas del cálculo (cuaderno de cálculos). Cada hoja es **un punto de operación**, no una serie temporal.
"""),
        C(r"""
CAMPOS = [("pozo", "Pozo", ""), ("bomba_referencia", "Bomba de referencia", ""), ("frecuencia_hz", "Frecuencia", "Hz"), ("etapas", "Etapas", ""),
          ("caudal_operacion_bfpd", "Caudal de operación", "BFPD"), ("presion_sensor_psi", "Presión de sensor", "psi"), ("thp_psi", "THP", "psi"),
          ("id_tubing_in", "Diámetro interior del tubing", "in"), ("temperatura_c", "Temperatura", "°C"), ("api_deg", "°API", "°API"), ("bsw_numero", "BS&W (número de la celda)", "rótulo «%»")]
ficha_pozos = pd.DataFrame({h["hoja"]: [h[k] for k, _, _ in CAMPOS] for h in hojas}, index=[f"{n} [{u}]" if u else n for _, n, u in CAMPOS]).reset_index().rename(columns={"index": "variable"})
T(ficha_pozos.astype(str), ancha=True)
"""),
        M(r"""
**Interpretación.** Las cinco hojas son **cinco pozos distintos** operando a frecuencias de 56 a 67 Hz, con 31 a 53 etapas, caudales de 5 419 a 10 301 BFPD, presión de sensor de 607 a 821 psi y THP de 145 a 210 psi. Dos referencias de bomba: `S 8000N` en tres pozos y `S6000N` en dos. Tres cosas llaman la atención y se registran sin concluir: (1) el diámetro interior del tubing (2.996 in) y el °API (12) son **idénticos en los cinco pozos**; (2) la temperatura toma solo dos valores (65.56 °C en cuatro hojas y 62.22 °C en una), que coinciden con 150 °F y 144 °F convertidos; y (3) el BS&W viene como número entre 0.9557 y 0.9766 con rótulo «%», lo que, leído como fracción, corresponde a cortes de agua de 95.6 % a 97.7 % (la ambigüedad del rótulo es la consulta CT-02). Que dos pozos distintos tengan la misma bomba y el mismo fluido no es un error por sí mismo; lo es **asumir** que son datos propios de cada pozo, pregunta que queda como CT-10.
"""),
        M(r"""
## Paso 4 · El survey: la trayectoria del pozo

**Qué es.** El *survey* es la tabla de mediciones de la trayectoria: para cada estación se registra la profundidad medida (MD, a lo largo del pozo), la inclinación respecto de la vertical, el azimut, la profundidad vertical (TVD) y la severidad de la curva (*dogleg*). Es la base para saber a qué profundidad **vertical** está cada equipo, y la presión de una columna de fluido depende de la vertical, no de la medida. Aquí solo se describe; el cuaderno de calidad lo verifica con la curvatura mínima.
"""),
        C(r"""
est = pd.DataFrame(estaciones)
res = est.groupby("hoja", sort=False).agg(estaciones=("md_ft", "size"), md_min_ft=("md_ft", "min"), md_max_ft=("md_ft", "max"),
                                           tvd_max_ft=("vertical_ft", "max"), inclinacion_max_deg=("inclinacion_deg", "max"),
                                           dogleg_max=("dogleg_deg_por_100ft", "max")).reset_index()
res["md_estrictamente_creciente"] = [bool((est[est.hoja == h].md_ft.diff().dropna() > 0).all()) for h in res.hoja]
T(res, ancha=True)
"""),
        C(r"""
rutas = guardar_figuras(hojas, estaciones)
display(Image(filename=str(RAIZ / "reports" / "figuras" / "survey_md_tvd_por_hoja.png")))
"""),
        C(r"""
display(Image(filename=str(RAIZ / "reports" / "figuras" / "inclinacion_survey_por_hoja.png")))
"""),
        M(r"""
**Interpretación de la tabla y de las dos figuras.** **Tabla.** Cada hoja tiene entre 56 y 71 estaciones, con MD que va de 0 a 4 530–4 637 ft y una TVD máxima de 2 765 a 3 016 ft. La inclinación máxima está entre 90.49° y 91.5°, es decir, los pozos terminan **prácticamente horizontales** (una inclinación algo mayor que 90° es normal en una sección lateral que sube ligeramente). La severidad máxima (*dogleg*) va de 4.98 a 8.35 °/100 ft. La MD crece estrictamente en las cinco hojas (sin estaciones repetidas ni desordenadas), condición necesaria para interpolar. **Figura 1 (MD frente a TVD).** En las cinco hojas la TVD crece casi linealmente con la MD hasta unos 3 000–3 500 ft de MD (sección inclinada que gana profundidad) y después se **aplana**: ahí empieza la sección horizontal, donde seguir avanzando en MD ya no aumenta la profundidad vertical. **Figura 2 (inclinación).** Cada caja resume las inclinaciones de las estaciones: la mediana está entre ≈28° y ≈46° y los extremos llegan a ≈0° y ≈91°, porque el pozo pasa de vertical a horizontal; no es una dispersión de datos sino la forma de la trayectoria. La comparación entre cajas muestra trayectorias de la misma familia, con diferencias de forma (por ejemplo, la caja de `QF-378HST` es la que llega a una inclinación menor en el tercer cuartil, ≈62°).
"""),
        M(r"""
## Paso 5 · Dónde están los equipos

**Qué se hace.** Para cada hoja se tabulan la profundidad medida (MD) y la vertical (TVD) de la **descarga** de la bomba, del **intake** (entrada de fluido) y del **sensor** de presión. **Por qué importa.** La presión que mide el sensor se traslada al intake con la columna de fluido entre ambos: lo que importa para esa corrección es la **diferencia de TVD**, no de MD.
"""),
        C(r"""
filas = []
for h in hojas:
    filas.append({"hoja": h["hoja"], "MD descarga": h["md_descarga_ft"], "MD intake": h["md_intake_ft"], "MD sensor": h["md_sensor_ft"],
                  "TVD descarga": h["tvd_descarga_ft"], "TVD intake": h["tvd_intake_ft"], "TVD sensor": h["tvd_sensor_ft"],
                  "TVD sensor − TVD intake": h["tvd_sensor_ft"] - h["tvd_intake_ft"], "MD sensor − MD intake": h["md_sensor_ft"] - h["md_intake_ft"],
                  "orden descarga < intake < sensor (TVD)": h["tvd_descarga_ft"] < h["tvd_intake_ft"] < h["tvd_sensor_ft"]})
equipos = pd.DataFrame(filas)
T(equipos, ancha=True)
"""),
        M(r"""
**Interpretación.** Los equipos están siempre ordenados: la descarga queda por encima del intake y el sensor por debajo, en las cinco hojas. El intake queda entre 5.6 y 8.4 ft (TVD) más profundo que la descarga y el sensor entre 19.3 y 25.6 ft (TVD) más profundo que el intake. **Lo importante está en las dos últimas columnas de distancia:** la separación sensor–intake en TVD (19–26 ft) es entre 0.45 y 0.62 veces la separación en MD (33–46 ft), porque en esos puntos el pozo todavía está inclinado. Si se usara la MD en lugar de la TVD para trasladar la presión entre el sensor y el intake, la columna de fluido considerada sería entre un 61 % y un 124 % mayor. Por eso el cálculo usa TVD y por eso el cuaderno de calidad comprueba que las TVD de los equipos salen del survey por interpolación.
"""),
        M(r"""
## Paso 6 · Criterios de aceptación
"""),
        C(r"""
crit = Criterios("01_inspeccion_BES_jun")
crit.comprobar("C01b-1", "Las cinco hojas tienen todos los bloques ubicados", bool(anclas.notna().all().all()) and anclas.shape[1] == 5, f"{anclas.shape[0]} rótulos × {anclas.shape[1]} hojas")
crit.comprobar("C01b-2", "Las cinco hojas comparten el número de columnas", comp["columnas"].nunique() == 1, f"columnas = {sorted(int(c) for c in comp['columnas'].unique())}")
crit.comprobar("C01b-3", "Orden descarga < intake < sensor en TVD en las cinco", bool(equipos["orden descarga < intake < sensor (TVD)"].all()), "5/5")
crit.comprobar("C01b-4", "MD del survey estrictamente creciente en cada hoja", bool(res["md_estrictamente_creciente"].all()), f"{int(res['estaciones'].sum())} estaciones")
crit.comprobar("C01b-5", "Las dos figuras existen", all((RAIZ / "reports" / "figuras" / n).is_file() for n in ("survey_md_tvd_por_hoja.png", "inclinacion_survey_por_hoja.png")), "2 figuras")
crit.comprobar("C01b-6", "El libro no cambió", huellas(COPIA_TRABAJO)["sha256"] == sha_inicial, sha_inicial[:16] + "…")
T(crit.tabla())
"""),
        C(r"""
crit.exigir()
print("Todos los criterios de aceptación del cuaderno 01 (inspección) se cumplen.")
"""),
        M(r"""
## Conclusión técnica

- **Resultado:** las cinco hojas son cálculos autónomos de 19 columnas y estructura común, pero con los bloques desplazados entre 1 y 3 filas, de modo que solo una lectura por rótulo es segura.
- **Qué describen los datos:** cinco pozos horizontales con survey de 56 a 71 estaciones, equipos en la sección inclinada, dos referencias de bomba y parámetros de fluido y tubing repetidos entre pozos.
- **Qué se deja anotado sin concluir:** valores idénticos entre pozos (CT-10), rótulo de BS&W (CT-02) y la composición distinta de bloques secundarios de `QF-549HST`.
- **Qué no se afirma:** nada sobre el estado de ningún pozo. Es un inventario descriptivo de un único punto de operación por hoja.
- **Siguiente paso:** `01_inspeccion_y_calidad_datos`, que somete lo aquí descrito a controles de calidad.
"""),
    ]


if __name__ == "__main__":
    print(guardar(NOMBRE, construir()))
