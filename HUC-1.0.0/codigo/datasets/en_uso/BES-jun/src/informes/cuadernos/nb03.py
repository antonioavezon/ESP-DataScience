"""Cuaderno 03: limpieza y mapeo de variables."""

from informes.cuadernos.base import C, M, PREPARACION, guardar

NOMBRE = "03_limpieza_y_mapeo"


def construir():
    return [
        M(r"""
# Cuaderno 03 · Limpieza y mapeo de variables

**Expediente:** BES-jun · **Cuaderno:** 4 de 7 · **Estado del expediente:** Listo para revisión (no Completo)

## 1. Introducción y contexto (el problema)
Los datos están en un formulario, no en una tabla. Para calcular, graficar y auditar hace falta una estructura donde **cada número tenga nombre, unidad, tipo (dato o fórmula) y la celda exacta de la que salió**. Si la conversión pierde esa procedencia, un valor sospechoso ya no puede rastrearse hasta su origen, y si «limpia» valores sin dejar registro, se destruye evidencia.

## 2. Justificación y necesidad
Una tabla larga (hoja × variable) con procedencia por celda, un registro de unidades que **señale** los rótulos engañosos sin corregirlos en silencio, y una política de transformaciones explícita y comprobable: qué se hizo y, sobre todo, qué **no** se hizo.

## 3. Objetivo general
Generar los archivos de variables y unidades del expediente y demostrar, con una prueba de ida y vuelta contra el libro, que ningún valor fue alterado.

## 4. Dominio y alcance
**Incluye:** 34 variables por hoja (entradas de operación, parámetros mecánicos, de fluido y de bomba, límites escritos, resultados de la hoja); celda de origen, tipo de celda y unidad rotulada; identificadores (hoja, Cluster, Pozo); comparación de los datos de prueba con los de operación; escritura de CSV y su relectura.

**No incluye:** convertir unidades, imputar faltantes, normalizar, redondear ni «corregir» valores; unir hojas en un solo registro (cada hoja es un punto de operación, no una serie); elegir la llave del registro (CT-01).

## 5. Fuentes y datos (entradas y salidas)
**Entrada:** `entrada/BES_jun.xlsx`. **Salidas:** `data_procesados/variables_largo.csv`, `data_procesados/matriz_entradas_por_hoja.csv`, `data_procesados/registro_unidades.csv`.

## 6. Objetivos específicos y criterios de aceptación
**C03-1** 170 filas (34 variables × 5 hojas) y ninguna celda sin encontrar · **C03-2** los valores del mapeo coinciden con los del lector del cuaderno 04 · **C03-3** la prueba de ida y vuelta contra el libro no encuentra diferencias · **C03-4** los CSV releídos coinciden con lo escrito · **C03-5** toda variable tiene unidad rotulada o está declarada adimensional · **C03-6** el libro no cambió.

## 7. Riesgo si este paso falla
Un valor mal asignado a una variable (el caudal de prueba por el de operación, un caché por un dato) contamina todo el cálculo. Si la tabla no conserva la celda de origen, el error no se puede encontrar; si el «mapeo» modificó valores, tampoco se puede saber cuál era el dato real.
"""),
        M(r"""
## Preparación del entorno
Misma celda que en los demás cuadernos. Se guarda la huella del libro antes de empezar para demostrar al final que no cambió.
"""),
        C(PREPARACION),
        C(r"""
from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO, leer_libro
sha_inicial = huellas(COPIA_TRABAJO)["sha256"]
hojas = leer_libro()
"""),
        M(r"""
## Paso 1 · Diccionario de variables

**Qué se hace.** Se declara, de forma explícita y en un solo lugar (`ingesta/mapeo.py`), qué variables se extraen y **cómo se localiza cada una**: por el texto de su rótulo, en qué columna está el rótulo, en cuál el valor y en cuál la unidad. **Por qué.** Un mapeo implícito (índices sueltos en el código) no es auditable. Aquí cada variable es una línea revisable: «el caudal de operación es la celda de la columna B de la fila cuyo rótulo en la columna A es *Caudal*, buscando desde la fila 60». La búsqueda desde la fila 60 evita confundirla con la celda «Caudal» del bloque de bomba, que está más arriba.
"""),
        C(r"""
from ingesta.mapeo import VARIABLES
dic = pd.DataFrame(VARIABLES, columns=["variable", "rótulo buscado", "col. rótulo", "col. valor", "col. unidad",
                                       "buscar desde fila", "n.º de aparición", "rol"])
dic["col. unidad"] = dic["col. unidad"].map(lambda v: "encabezado de tabla" if v is None else v)
print("Variables declaradas:", len(dic))
T(dic, ancha=True)
"""),
        M(r"""
**Cómo leer la tabla.** «n.º de aparición = 2» (caso de la temperatura en °C) significa que el rótulo «Temperatura de fondo» aparece dos veces —la primera en °F, la segunda en °C como fórmula— y se toma la segunda. Las variables con prefijo `cache_` son **resultados que la propia hoja calculó**; se extraen para poder contrastarlos con el código (cuaderno 04), no para usarlos como entradas.
"""),
        M(r"""
## Paso 2 · Ejecutar el mapeo: tabla larga con procedencia

La tabla larga tiene una fila por hoja y variable, con: celda de origen (`G26`), tipo de celda (**constante** escrita a mano o **fórmula** calculada por Excel), fórmula (si la hay), valor, unidad rotulada y rol. Para fórmulas el valor es el **guardado en caché** del último cálculo de Excel.
"""),
        C(r"""
from ingesta.mapeo import mapear
largo = pd.DataFrame(mapear())
print("Filas:", len(largo), "| hojas:", largo["hoja"].nunique(), "| variables:", largo["variable"].nunique(),
      "| celdas no encontradas:", int((largo["tipo_celda"] == "no encontrada").sum()))
print("Tipo de celda:", largo["tipo_celda"].value_counts().to_dict())
T(largo[largo["hoja"] == "QF-554H"][["variable", "rotulo", "celda", "tipo_celda", "valor", "unidad_rotulada", "rol"]]
  .rename(columns={"rotulo": "rótulo en la hoja"}), ancha=True)
"""),
        M(r"""
Arriba se muestra la hoja QF-554H como ejemplo; las otras cuatro tienen la misma forma con **otra celda de origen** para cada variable. A continuación, la **matriz de entradas**: una variable por fila y una hoja por columna, para comparar de un vistazo las cinco condiciones de operación.
"""),
        C(r"""
matriz = largo.pivot(index="variable", columns="hoja", values="valor")[[h["hoja"] for h in hojas]]
matriz = matriz.loc[[v for v in dic["variable"]]].reset_index()
T(matriz, ancha=True)
"""),
        M(r"""
**Lectura rápida de la matriz.** Las cinco hojas operan a frecuencias distintas de la de la curva (60 Hz), tienen entre 31 y 53 etapas y sus límites de caudal escritos son iguales por grupos (2500/8000/10000 en tres hojas; 2000/6000/8000 en dos), lo que corresponde a la misma referencia de bomba (cuaderno 06 lo verifica con las tablas). Falta mirar lo contrario: ¿qué **no varía** entre pozos?
"""),
        C(r"""
cols = [h["hoja"] for h in hojas]
fijas = matriz[matriz[cols].nunique(axis=1) == 1][["variable", cols[0]]].rename(columns={cols[0]: "valor (igual en las 5 hojas)"})
fijas = fijas[~fijas["variable"].str.startswith("cache_")]
print("Variables de entrada con el mismo valor en las 5 hojas:", len(fijas))
T(fijas)
"""),
        M(r"""
**Hallazgo.** °API (12), presión de yacimiento (1100 psi), presión de burbuja (130 psi), densidad del agua (8.345 lb/gal), ID del tubing (2.996 in) y la frecuencia de la curva son **idénticos en los cinco pozos**. Para el ID y la frecuencia de la curva es razonable (misma completación y misma tabla). Para **°API, yacimiento y burbuja** es llamativo: cinco pozos distintos con exactamente el mismo fluido y la misma presión de yacimiento sugiere valores de **plantilla** más que mediciones por pozo. No se concluye que estén mal; se registra como riesgo, porque °API alimenta directamente el gradiente (y con él PIP, THP y THD). Debe confirmarse con quien mantiene el libro si esos datos son propios de cada pozo.
"""),
M(r"""
## Paso 3 · Prueba de ida y vuelta contra el libro

**Qué se prueba.** Que la tabla larga es una **copia fiel**. Se vuelve a abrir el libro y, para cada fila, se lee otra vez la celda indicada en `celda` y se compara con el `valor` de la tabla (el crudo si es constante; el guardado en caché si es fórmula). Si el mapeo hubiera redondeado, convertido o mal asignado algo, aparecería aquí. Es una prueba **independiente de la lógica de búsqueda**: usa solo la dirección de celda resultante.
"""),
        C(r"""
from openpyxl import load_workbook
wf = load_workbook(COPIA_TRABAJO, data_only=False)
wv = load_workbook(COPIA_TRABAJO, data_only=True)
diferencias = []
for fila in largo.itertuples():
    crudo, cache = wf[fila.hoja][fila.celda].value, wv[fila.hoja][fila.celda].value
    esperado = cache if fila.tipo_celda == "fórmula" else crudo
    if esperado != fila.valor:
        diferencias.append((fila.hoja, fila.variable, fila.celda, esperado, fila.valor))
wf.close(); wv.close()
print("Filas comprobadas:", len(largo), "| diferencias encontradas:", len(diferencias))
"""),
        M(r"""
**Interpretación.** Cero diferencias: cada valor de la tabla es **exactamente** el de su celda, con la misma precisión de punto flotante. El mapeo no transformó nada.
"""),
        M(r"""
## Paso 4 · Identificadores: hoja, Cluster y Pozo

El libro tiene tres textos que parecen identificar el registro: el **nombre de la hoja**, la celda **Cluster** y la celda **Pozo**. Antes de elegir una llave hay que ver si coinciden.
"""),
        C(r"""
ids = pd.DataFrame([{"hoja": h["hoja"], "Cluster": h["cluster"], "Pozo": h["pozo"],
                     "Cluster = hoja": h["cluster"] == h["hoja"], "llave compuesta usada": h["llave"]} for h in hojas])
print("Pozos distintos:", ids["Pozo"].nunique(), "de", len(ids), "| Cluster = nombre de hoja en todas:", bool(ids["Cluster = hoja"].all()))
T(ids)
"""),
        M(r"""
**Interpretación.** `Cluster` repite el nombre de la hoja (no aporta información nueva) y `Pozo` es otro código. El libro **no declara cuál es la llave** del registro (CT-01). Mientras tanto el expediente identifica cada punto por la **hoja**, que es única y es lo único verificable, y conserva `Pozo` como texto. No se afirma que la hoja y el pozo sean equivalentes.
"""),
        M(r"""
## Paso 5 · Registro de unidades

**Qué se hace.** Para cada variable se reúnen los rótulos de unidad que las cinco hojas escriben. Si una variable tuviera rótulos distintos entre hojas, la unidad sería ambigua. Después se añade una **observación** donde el rótulo es engañoso. **Qué no se hace:** no se convierte ninguna unidad; el valor se conserva con el rótulo que trae la hoja, y la observación advierte cómo interpretarlo.
"""),
        C(r"""
OBSERVACION = {
    "bsw_numero": "Rótulo «%», pero el número es una fracción (0.96–0.98) y la fórmula lo usa como tal. No se convierte (CT-02).",
    "cache_gradiente_psi_ft": "Rótulo «psi*ft»; por análisis dimensional es psi/ft (cuaderno 02).",
    "cache_densidad_lb_gal": "Rótulos «Lb/Gln» y «Lb/Galn» según la hoja: grafías de lb/gal.",
    "densidad_agua_lb_gal": "Rótulos «Lb/gln» y «Lb/galn» según la hoja: grafías de lb/gal.",
    "etapas": "Rótulo «Nº»: conteo adimensional.",
    "cache_sg_60": "Sin rótulo de unidad: gravedad específica, adimensional.",
    "cache_sg_temperatura": "Sin rótulo de unidad: gravedad específica, adimensional.",
}
ADIMENSIONALES = {"cache_sg_60", "cache_sg_temperatura"}
unidades = (largo.groupby("variable", sort=False)
            .agg(unidades_rotuladas=("unidad_rotulada", lambda s: " | ".join(sorted({str(u) for u in s if pd.notna(u)})) or "—"),
                 n_rotulos_distintos=("unidad_rotulada", lambda s: len({u for u in s if pd.notna(u)})),
                 tipo_de_celda=("tipo_celda", lambda s: " | ".join(sorted(set(s)))))
            .reset_index())
unidades["observación"] = unidades["variable"].map(OBSERVACION).fillna("")
sin_unidad = [v for v, u in zip(unidades["variable"], unidades["unidades_rotuladas"]) if u == "—"]
print("Variables con más de un rótulo de unidad entre hojas:", int((unidades["n_rotulos_distintos"] > 1).sum()))
print("Variables sin rótulo de unidad:", sin_unidad)
T(unidades.drop(columns="n_rotulos_distintos"), ancha=True)
"""),
        M(r"""
**Interpretación.** Solo dos variables muestran más de un rótulo entre hojas, y son **grafías de la misma unidad** (lb/gal escrita «Lb/gln», «Lb/galn» o «Lb/Gln»): no hay ambigüedad física. Dos variables no tienen rótulo y son gravedades específicas (adimensionales por definición). Tres rótulos merecen advertencia —`BS&W «%»`, `gradiente «psi*ft»` y las grafías de lb/gal—. Además, el caudal de operación y el de prueba son **constante en unas hojas y fórmula en otra** (columna «tipo de celda»): es la hoja con el factor 24 (CT-07). Esta tabla es la que debe consultar quien lea un resultado: indica no solo la unidad, sino **cuándo no creer el rótulo**.
"""),
        M(r"""
## Paso 6 · Datos de prueba frente a datos de operación

Cada hoja trae un caudal y una presión «de prueba» además de los de «operación». Si fueran iguales, la hoja no tendría información de **dos momentos**; si difieren, hay que saber cuánto. Es información relevante para evaluar (cuaderno 05) y para detectar celdas con fórmulas escondidas (CT-07).
"""),
        C(r"""
filas = []
for h in hojas:
    sub = largo[largo["hoja"] == h["hoja"]].set_index("variable")
    filas.append({"hoja": h["hoja"],
                  "Q prueba (BFPD)": h["caudal_prueba_bfpd"], "Q operación (BFPD)": h["caudal_operacion_bfpd"],
                  "diferencia Q (%)": 100 * (h["caudal_operacion_bfpd"] - h["caudal_prueba_bfpd"]) / h["caudal_prueba_bfpd"],
                  "P prueba (psi)": h["presion_prueba_psi"], "P sensor (psi)": h["presion_sensor_psi"],
                  "tipo de celda Q prueba": sub.loc["caudal_prueba_bfpd", "tipo_celda"],
                  "fórmula de Q prueba": sub.loc["caudal_prueba_bfpd", "formula"] or "—"})
prueba = pd.DataFrame(filas)
T(prueba, ancha=True)
"""),
        M(r"""
**Interpretación.** En las hojas donde el caudal de prueba coincide con el de operación, los datos de «prueba» y de «operación» **son el mismo punto**: no hay dos momentos que comparar. La excepción es la hoja cuya celda de prueba es una **fórmula** con un factor 24 sin definir (CT-07): allí prueba y operación difieren en una fracción de porcentaje. Además, en QF-545H la presión de prueba (654 psi) difiere de la del sensor (667 psi) con el mismo caudal. El expediente usa siempre los valores de **operación**; no redefine los de prueba.
"""),
        M(r"""
## Paso 7 · Guardar las tablas y verificarlas

Se escriben tres CSV en `data_procesados/` y se **releen** para comprobar que lo guardado es lo calculado. Un archivo que no se relee es un archivo del que se asume que está bien.
"""),
        C(r"""
import numpy as np
destino = RAIZ / "data_procesados"
largo.to_csv(destino / "variables_largo.csv", index=False)
matriz.to_csv(destino / "matriz_entradas_por_hoja.csv", index=False)
unidades.to_csv(destino / "registro_unidades.csv", index=False)

rel_largo = pd.read_csv(destino / "variables_largo.csv")
rel_matriz = pd.read_csv(destino / "matriz_entradas_por_hoja.csv")
rel_uni = pd.read_csv(destino / "registro_unidades.csv")
valores_ok = np.allclose(pd.to_numeric(rel_largo["valor"], errors="coerce").to_numpy(),
                         pd.to_numeric(largo["valor"], errors="coerce").to_numpy(), rtol=1e-12, atol=0, equal_nan=True)
csv_ok = (rel_largo.shape == largo.shape and rel_matriz.shape == matriz.shape and rel_uni.shape == unidades.shape
          and valores_ok and list(rel_largo["celda"]) == list(largo["celda"]))
print("Archivos escritos:", [p.name for p in sorted(destino.glob("*.csv")) if p.name in
      ("variables_largo.csv", "matriz_entradas_por_hoja.csv", "registro_unidades.csv")])
print("Relectura idéntica a lo escrito:", "SÍ" if csv_ok else "NO")
"""),
        M(r"""
## Paso 8 · Política de transformaciones

| Operación | ¿Se hizo? | Detalle |
|---|---|---|
| Cambiar de formulario a tabla larga | **Sí** | Una fila por hoja y variable, con celda de origen. |
| Convertir unidades (p. ej. °F → °C, % → fracción) | **No** | El valor se conserva con su rótulo. La temperatura en °C es la celda de **fórmula** de la propia hoja, no una conversión nuestra. |
| Imputar o rellenar faltantes | **No** | No hay faltantes (cuaderno 01); si los hubiera, la variable queda vacía. |
| Redondear o normalizar | **No** | Precisión de punto flotante completa. |
| Eliminar filas, outliers o hojas | **No** | Se conservan las cinco hojas. |
| Unir hojas | **No** | Cada hoja es un punto de operación aislado; no se construye una «serie». |
| Guardar el libro | **No** | `openpyxl` solo lee; el SHA-256 se verifica al final. |

Esta política es deliberadamente conservadora: **ante la duda, se registra y se pregunta; no se corrige en silencio**. Cualquier transformación futura debe añadirse a esta tabla antes de aplicarse.
"""),
        M(r"""
## Paso 9 · Criterios de aceptación
"""),
        C(r"""
crit = Criterios("03_limpieza_y_mapeo")
n_comunes = 0
for h in hojas:
    sub = largo[largo["hoja"] == h["hoja"]].set_index("variable")["valor"]
    for clave, valor in h.items():
        if clave in sub.index and isinstance(valor, (int, float)) and isinstance(sub[clave], (int, float)):
            n_comunes += 1
            if abs(float(sub[clave]) - float(valor)) > 1e-12:
                diferencias.append((h["hoja"], clave, "lector", valor, sub[clave]))
crit.comprobar("C03-1", "170 filas y ninguna celda sin encontrar", len(largo) == 5 * len(VARIABLES) == 170
               and int((largo["tipo_celda"] == "no encontrada").sum()) == 0, f"{len(largo)} filas")
crit.comprobar("C03-2", "Mapeo = lector en las variables comunes", n_comunes > 100 and not [d for d in diferencias if d[2] == "lector"],
               f"{n_comunes} valores comparados")
crit.comprobar("C03-3", "Ida y vuelta contra el libro sin diferencias", not [d for d in diferencias if d[2] != "lector"],
               f"{len(largo)} celdas releídas")
crit.comprobar("C03-4", "CSV releídos idénticos a lo escrito", csv_ok, "3 archivos")
crit.comprobar("C03-5", "Toda variable tiene unidad o está declarada adimensional", set(sin_unidad) <= ADIMENSIONALES,
               f"sin rótulo: {sin_unidad}")
crit.comprobar("C03-6", "El libro no cambió", huellas(COPIA_TRABAJO)["sha256"] == sha_inicial, sha_inicial[:16] + "…")
T(crit.tabla())
"""),
        C(r"""
crit.exigir()
print("Todos los criterios de aceptación del cuaderno 03 se cumplen.")
"""),
        M(r"""
## Conclusión técnica

- **Resultado:** quedó una tabla larga de 170 filas con la celda de origen de cada número, comprobada celda por celda contra el libro, y un registro de unidades que advierte los tres rótulos engañosos.
- **Qué habilita:** cualquier valor que aparezca en un informe puede rastrearse hasta una celda concreta de una hoja concreta del archivo identificado por su SHA-256.
- **Lo que no se resolvió (y se declara):** la llave del registro (CT-01); la unidad real de BS&W (CT-02); el significado del factor 24 (CT-07).
- **Límites:** el mapeo localiza por rótulo; si una versión futura del libro cambiara un rótulo, la variable aparecería como «no encontrada» y el criterio C03-1 detendría la ejecución, en lugar de leer otra celda sin avisar.
- **Siguiente paso:** cuaderno 04, ejecución de la cadena de cálculo y contraste de cada paso intermedio con la hoja.
"""),
    ]


if __name__ == "__main__":
    print(guardar(NOMBRE, construir()))
