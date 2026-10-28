"""Cuaderno 02: trazabilidad y análisis de las fórmulas."""

from informes.cuadernos.base import C, M, PREPARACION, guardar

NOMBRE = "02_trazabilidad_y_analisis_formulas"


def construir():
    return [
        M(r"""
# Cuaderno 02 · Trazabilidad y análisis de las fórmulas

**Expediente:** BES-jun · **Cuaderno:** 3 de 7 · **Estado del expediente:** Listo para revisión (no Completo)

## 1. Introducción y contexto (el problema)
La cadena que produce PIP, THD y caudal a producir está escrita **dentro de celdas de Excel**, con constantes incrustadas en las fórmulas, rótulos de unidad que no siempre corresponden a lo que se calcula y diferencias con los documentos de referencia. Si se copia una fórmula sin entenderla, se copian también sus errores: un signo invertido o un exponente distinto produce números de apariencia normal y sentido físico incorrecto.

## 2. Justificación y necesidad
Construir un registro de trazabilidad: para cada fórmula de la cadena, **dónde está, qué calcula, con qué constantes, en qué unidades y con qué respaldo**. Verificar que la fórmula es la misma en las cinco hojas (para poder transcribirla una sola vez), y detectar con evidencia numérica las discrepancias que pueden alterar resultados.

## 3. Objetivo general
Dejar cada fórmula de la cadena clasificada (utilizable / utilizable con reserva / fuera de alcance) con su fuente, sus constantes y sus reservas enlazadas a consultas técnicas (CT-xx), y cuantificar la inconsistencia hidrostática del signo de PIP.

## 4. Dominio y alcance
**Incluye:** 9 celdas de la cadena (gravedad a 60 °F y a temperatura, densidad, gradiente, PIP, THP, fricción, THD, caudal a producir); firma estructural entre hojas; inventario de constantes; análisis dimensional de rótulos; consistencia hidrostática; discrepancias con el PDF 004; catálogo de fórmulas.

**No incluye:** ejecutar las fórmulas (cuaderno 04); cuantificar el impacto de cada discrepancia sobre los resultados (cuaderno 05); el bloque de potencia, motor y cable (sus constantes no tienen origen documentado: quedan fuera de alcance); elegir un signo, un exponente o una constante «correctos».

## 5. Fuentes y datos (entradas y salidas)
**Entradas:** `entrada/BES_jun.xlsx`; `docs/trazabilidad_ecuaciones.md`; `docs/consultas_tecnicas_pendientes.md`. **Salidas:** tablas de celdas, firmas, constantes, rótulos, hidrostática, discrepancias y catálogo.

## 6. Objetivos específicos y criterios de aceptación
**C02-1** las 9 fórmulas tienen firma idéntica en las 5 hojas · **C02-2** toda constante literal está clasificada · **C02-3** el exponente de fricción es el mismo en las 5 hojas y la diferencia con el PDF está registrada · **C02-4** la consistencia hidrostática del signo de PIP se evaluó en las 5 hojas y quedó registrada · **C02-5** cada reserva del catálogo remite a una consulta existente.

## 7. Riesgo si este paso falla
Transcribir mal una fórmula, o transcribirla bien pero sin advertir que contradice la física elemental, y presentar el resultado como confiable. Un PIP sobrestimado hace parecer que la bomba trabaja con más presión de admisión de la real; una decisión basada en ello puede llevar a operar fuera de condiciones seguras sin ninguna alarma.
"""),
        M(r"""
## Preparación del entorno
Misma celda que en los demás cuadernos: localiza el expediente y registra la ficha de reproducibilidad.
"""),
        C(PREPARACION),
        M(r"""
## Paso 1 · Localizar la cadena de cálculo en cada hoja

**Qué se hace.** Se identifican, por **rótulo** (cuaderno 01), las nueve celdas de la cadena en cada hoja. Los identificadores (`B96`, `G102`...) son las direcciones de la hoja de referencia **QF-554H**; en las otras hojas la fila cambia pero el concepto es el mismo. **Por qué.** Sin una dirección concreta por hoja no se puede decir «esta fórmula es la que se transcribió».
"""),
        C(r"""
from openpyxl import load_workbook
from ingesta.leer_bes_jun import COPIA_TRABAJO, buscar_en_columna, leer_libro

hojas = leer_libro()
# id (dirección en QF-554H), rótulo, columna del rótulo, columna del valor, fila desde la que buscar
CADENA = [
    ("B96",  "Gravedad Oil @ 60ºF",    1, "B", 60),
    ("B98",  "Gravedad Oil @ T fondo", 1, "B", 60),
    ("B100", "Densidad de Fluido",     1, "B", 60),
    ("B102", "Gradiente de Presión",   1, "B", 60),
    ("G96",  "PIP en (ft)",            5, "G", 1),
    ("G98",  "THP en (ft)",            5, "G", 1),
    ("G100", "Perdidad por Fricción",  5, "G", 1),
    ("G102", "THD TOTAL",              5, "G", 1),
    ("B106", "Caudal a producir",      1, "B", 60),
]
wf = load_workbook(COPIA_TRABAJO, data_only=False)
celdas = {}
for ws in wf.worksheets:
    celdas[ws.title] = {}
    for id_, rotulo, col, letra, desde in CADENA:
        fila = buscar_en_columna(ws, col, rotulo, desde=desde)
        celdas[ws.title][id_] = f"{letra}{fila}"
ubicacion = pd.DataFrame([{"id (en QF-554H)": id_, "rótulo": rotulo, **{h: celdas[h][id_] for h in celdas}}
                          for id_, rotulo, *_ in CADENA])
T(ubicacion)
"""),
        C(r"""
ws_ref = wf["QF-554H"]
T(pd.DataFrame([{"celda": id_, "rótulo": rotulo, "fórmula escrita en la hoja": ws_ref[id_].value}
                for id_, rotulo, *_ in CADENA]))
"""),
        M(r"""
**Cómo leer las fórmulas.** Las cuatro primeras construyen el **gradiente de presión del fluido** a partir de °API, temperatura, BS&W y densidad del agua. `PIP en (ft)`, `THP en (ft)` y `Perdidad por Fricción` (el rótulo de la hoja tiene esa errata y se conserva) alimentan `THD TOTAL`, que es la altura que debe vencer la bomba. `Caudal a producir` (`=K94`) viene de la intersección de esa THD con la curva de la bomba; su cálculo está en un bloque de `MATCH`/`INDEX` que el cuaderno 04 transcribe.
"""),
        M(r"""
## Paso 2 · ¿Es la misma fórmula en las cinco hojas?

**Por qué importa.** El código transcribe cada fórmula **una vez**. Eso solo es legítimo si las cinco hojas calculan lo mismo. Comparar texto de fórmula no sirve (las filas cambian), así que se usa una **firma estructural**: el esqueleto de la fórmula (operadores, funciones y constantes, con cada referencia sustituida por `@`) más, para cada referencia, la columna y el **rótulo** de su fila. Dos hojas con la misma firma calculan lo mismo con las mismas constantes y leen los mismos conceptos.
"""),
        C(r"""
from analisis.dependencias import firma_estructural
filas = []
for id_, rotulo, *_ in CADENA:
    firmas = {h: firma_estructural(wf[h], celdas[h][id_]) for h in celdas}
    distintas = len(set(firmas.values()))
    esq, refs = firmas["QF-554H"]
    filas.append({"celda": id_, "firmas distintas entre hojas": distintas, "idéntica en 5 hojas": distintas == 1,
                  "esqueleto": esq, "referencias (columna|rótulo)": "; ".join(refs)})
firmas_tabla = pd.DataFrame(filas)
T(firmas_tabla[["celda", "firmas distintas entre hojas", "idéntica en 5 hojas"]])
"""),
        C(r"""
T(firmas_tabla[["celda", "esqueleto", "referencias (columna|rótulo)"]], ancha=True)
"""),
        M(r"""
**Interpretación.** Las nueve fórmulas tienen **una única firma** en las cinco hojas: misma estructura, mismas constantes y mismos conceptos de entrada. Transcribirlas una vez es legítimo. La segunda tabla es la fórmula **leída en lenguaje de rótulos**: por ejemplo `PIP en (ft)` usa `B|Presión de Sensor`, la diferencia `C|Intake − C|Sensor` y `B|Gradiente de Presión` dos veces. Esa lectura es la que se revisa contra la física en el Paso 5.

*Alcance de la prueba:* la igualdad de firma garantiza igualdad **de estructura**; no garantiza que los valores de entrada sean correctos (cuaderno 01) ni que la fórmula sea físicamente adecuada (Pasos 4 y 5).
"""),
        M(r"""
## Paso 3 · Constantes escritas dentro de las fórmulas

**Riesgo específico.** Una constante incrustada en una fórmula no aparece como dato en ninguna celda: no se puede auditar buscando entradas. Se extraen todos los números literales de las nueve fórmulas y se clasifica cada uno según lo que **está documentado** en `docs/trazabilidad_ecuaciones.md` y en el PDF 004. La categoría «sin origen documentado» **no significa que esté mal**: significa que el expediente no puede respaldarlo con una fuente.
"""),
        C(r"""
from collections import Counter
from analisis.dependencias import constantes_literales

ORIGEN = {
    141.5: ("F-01 (API → gravedad), X1 J4 y QF-554H!B96", "documentada"),
    131.5: ("F-01 (API → gravedad), X1 J4 y QF-554H!B96", "documentada"),
    0.00066: ("Corrección de temperatura de B98", "sin origen documentado (CT-04)"),
    3e-07: ("Corrección de temperatura de B98", "sin origen documentado (CT-04)"),
    15.556: ("Corrección de temperatura de B98 (referencia de temperatura en °C)", "sin origen documentado (CT-04)"),
    8.33: ("Densidad de mezcla de B100; aparece como divisor y como multiplicador", "sin origen documentado"),
    0.052: ("Gradiente de B102 (densidad × 0.052)", "escrita en la celda; sin origen documentado fuera de ella"),
    2.083: ("Hazen-Williams, PDF 004 p. 2", "documentada (PDF)"),
    100.0: ("Hazen-Williams: (100/C)^1.85", "documentada (PDF)"),
    120.0: ("Hazen-Williams: coeficiente C = 120", "documentada (PDF, ejemplo)"),
    1.85: ("Hazen-Williams: exponente de (100/C) y de (Q/34.3)", "documentada (PDF)"),
    34.3: ("Hazen-Williams: normalización de Q", "documentada (PDF)"),
    1000.0: ("Pérdida en ft por cada 1000 ft de longitud", "documentada (PDF)"),
    4.8566: ("Exponente del ID en Hazen-Williams", "la celda dice 4.8566; el PDF dice 4.8655 (CT-05)"),
    1.0: ("Aritmética: 1 − BS&W, 1/ID, J95+1", "aritmética"),
    2.0: ("Aritmética: cuadrado en la corrección de temperatura", "aritmética"),
}
filas = []
for id_, rotulo, *_ in CADENA:
    cuentas = Counter(constantes_literales(wf["QF-554H"][id_].value))
    for valor, veces in sorted(cuentas.items()):
        origen, estado = ORIGEN.get(valor, ("—", "SIN CLASIFICAR"))
        filas.append({"celda": id_, "constante": valor, "veces": veces, "dónde se usa": origen, "estado": estado})
constantes = pd.DataFrame(filas)
print("Constantes literales encontradas:", len(constantes), "| sin clasificar:", int((constantes["estado"] == "SIN CLASIFICAR").sum()))
T(constantes, ancha=True)
"""),
        M(r"""
**Interpretación.** Todas las constantes quedaron clasificadas. Tres grupos requieren atención:

1. **Corrección de temperatura (`0.00066`, `0.0000003`, `15.556`).** Sin origen documentado. La corrección es pequeña (cuaderno 05 cuantifica su efecto), pero se transcribe tal cual y se registra como **CT-04**.
2. **`8.33` y `0.052`.** Son factores de conversión de unidades de uso corriente en campo, pero ninguna fuente leída del expediente los define; se transcriben sin sustituirlos por `0.433` ni `8.34`.
3. **`4.8566`.** El PDF de diseño escribe **4.8655**. Las dos cifras difieren en los últimos dígitos, lo que podría ser un error de tipeo en cualquiera de los dos documentos (o una diferencia deliberada que no está explicada). Es la discrepancia **CT-05**; el código usa el valor de la hoja y el cuaderno 05 mide cuánto cambia si fuera el otro.

Además, el PDF indica que Hazen-Williams está planteado para **agua a 20 °C**; en estas hojas el fluido es una mezcla con °API = 12 y BS&W entre 0.96 y 0.98. La aplicabilidad de la ecuación a ese fluido es una reserva adicional de CT-05, no una conclusión.
"""),
        M(r"""
## Paso 4 · Análisis dimensional de los rótulos

**Qué se hace.** Se compara el rótulo de unidad que la hoja escribe junto a cada resultado con la unidad que **resulta** de la propia fórmula. **Por qué.** Un rótulo equivocado es inofensivo para Excel pero peligroso para quien lo lee: ya hay un caso (BS&W) donde el rótulo contradice el uso del número.
"""),
        C(r"""
def rotulo_a_la_derecha(hoja, id_, col_unidad):
    ws = wf[hoja]
    fila = int("".join(ch for ch in celdas[hoja][id_] if ch.isdigit()))
    return ws.cell(fila, col_unidad).value

h0 = hojas[0]
analisis_unidades = pd.DataFrame([
    {"variable": "BS&W", "rótulo en la hoja": h0["bsw_unidad_rotulo"],
     "unidad según la fórmula": "fracción adimensional (la fórmula usa 1 − BS&W)",
     "coherente": h0["bsw_unidad_rotulo"] != "%", "consecuencia": "no se convierte; consulta CT-02"},
    {"variable": "Densidad de Fluido (B100)", "rótulo en la hoja": rotulo_a_la_derecha("QF-554H", "B100", 3),
     "unidad según la fórmula": "lb/gal (8.33 × adimensional)",
     "coherente": True, "consecuencia": "ninguna; el rótulo es una grafía de lb/gal"},
    {"variable": "Gradiente de Presión (B102)", "rótulo en la hoja": rotulo_a_la_derecha("QF-554H", "B102", 3),
     "unidad según la fórmula": "psi/ft (lb/gal × 0.052)",
     "coherente": False, "consecuencia": "«psi*ft» es un producto, no un gradiente; el resultado es psi/ft"},
    {"variable": "PIP en (ft)", "rótulo en la hoja": rotulo_a_la_derecha("QF-554H", "G96", 8),
     "unidad según la fórmula": "ft de columna (psi ÷ psi/ft)", "coherente": True, "consecuencia": "ninguna"},
    {"variable": "Caudal a producir (B106)", "rótulo en la hoja": rotulo_a_la_derecha("QF-554H", "B106", 3),
     "unidad según la fórmula": "BFPD (interpolado de la tabla de caudal)", "coherente": True, "consecuencia": "ninguna"},
])
T(analisis_unidades, ancha=True)
"""),
        M(r"""
**Interpretación.** Dos rótulos son engañosos: **BS&W «%»** (el número es una fracción de 0.96–0.98 y la fórmula lo usa como tal; si se dividiera entre 100 se obtendría un fluido casi sin agua, físicamente distinto) y **gradiente «psi\*ft»** (es psi/ft). Ninguno cambia el cálculo, pero ambos pueden inducir a un error de lectura o de conversión de quien consuma el resultado, por eso el código **rotula las unidades correctas** en sus salidas y el diccionario de datos documenta el rótulo original.
"""),
        M(r"""
## Paso 5 · Consistencia hidrostática del signo de PIP (CT-03)

**Premisa física.** En un fluido, la presión **aumenta con la profundidad**. Si el sensor está más profundo que el intake de la bomba, la presión en el intake debe ser **menor** que la medida por el sensor: `P_intake ≈ P_sensor − gradiente · (TVD_sensor − TVD_intake)`.

**Lo que escribe la hoja.** `PIP en (ft) = (P_sensor − ((TVD_intake − TVD_sensor) · gradiente)) / gradiente`. Con el sensor más profundo, `(TVD_intake − TVD_sensor)` es negativo y el signo menos lo vuelve **positivo**: la fórmula **suma** la corrección. Se convierte el resultado de la hoja a psi (`PIP_ft × gradiente`) y se compara con la presión del sensor. El argumento es de **signo**, no de magnitud: no se afirma que el valor hidrostático simple sea el verdadero, solo que el sentido de la corrección que escribe la hoja es opuesto al esperable.
"""),
        C(r"""
from modelo_deterministico.fluidos_bes_jun import evaluar_fluido
filas = []
for h in hojas:
    g = evaluar_fluido(h["api_deg"], h["temperatura_c"], h["bsw_numero"], h["densidad_agua_lb_gal"]).resultados["gradiente_psi_ft"]["valor"]
    dz = h["tvd_sensor_ft"] - h["tvd_intake_ft"]                 # > 0: el sensor está más profundo
    pip_psi_hoja = h["cache_pip_ft"] * g                         # lo que la celda implica, en psi
    p_hidrostatica = h["presion_sensor_psi"] - g * dz            # presión en el intake por hidrostática simple
    filas.append({"hoja": h["hoja"], "TVD sensor − TVD intake (ft)": dz, "P sensor (psi)": h["presion_sensor_psi"],
                  "PIP de la hoja en psi": pip_psi_hoja, "P en intake, hidrostática (psi)": p_hidrostatica,
                  "diferencia hoja − hidrostática (psi)": pip_psi_hoja - p_hidrostatica,
                  "sensor más profundo": dz > 0, "PIP de la hoja > P sensor": pip_psi_hoja > h["presion_sensor_psi"]})
hidro = pd.DataFrame(filas)
T(hidro, ancha=True)
"""),
        M(r"""
**Interpretación.** En las **cinco** hojas el sensor está más profundo que el intake y, aun así, la celda entrega en el intake una presión **mayor** que la del sensor. La diferencia entre lo que escribe la hoja y la hidrostática simple es de entre 17 y 22 psi según la hoja (≈ `2 · gradiente · ΔTVD`). Esto **no demuestra** que la hoja esté equivocada: podría usar una convención que el libro no declara. Pero sí hace de CT-03 la **reserva de mayor prioridad** del expediente, porque (a) la analogía F-12 del plan escribe la corrección con el signo contrario, que es consistente con la hidrostática, y (b) el cuaderno 05 muestra que este signo mueve el caudal calculado en una magnitud comparable a la diferencia calculado-medido.

**Decisión de trabajo.** El código **conserva el signo de la hoja** (se transcribe, no se corrige por criterio propio) y toda salida de PIP lleva la advertencia. La consulta técnica CT-03 debe resolverse con quien mantiene el libro **antes** de usar el PIP para cualquier decisión.
"""),
        M(r"""
## Paso 6 · Registro de discrepancias con evidencia numérica
"""),
        C(r"""
exponentes = {h: sorted(set(c for c in constantes_literales(wf[h][celdas[h]["G100"]].value) if 4 < c < 5)) for h in celdas}
temperatura = {h: sorted(set(c for c in constantes_literales(wf[h][celdas[h]["B98"]].value) if c in (0.00066, 3e-07, 15.556))) for h in celdas}
discrepancias = pd.DataFrame([
    {"id": "CT-03", "discrepancia": "Signo de la corrección de PIP opuesto a la hidrostática y a F-12",
     "evidencia": f"{int(hidro['PIP de la hoja > P sensor'].sum())} de {len(hidro)} hojas con PIP > P sensor y sensor más profundo",
     "prioridad": "alta"},
    {"id": "CT-05", "discrepancia": "Exponente del ID en Hazen-Williams: hoja vs PDF 004",
     "evidencia": f"hoja: {sorted({v for lista in exponentes.values() for v in lista})}; PDF: [4.8655]; igual en las 5 hojas: {len({tuple(v) for v in exponentes.values()}) == 1}",
     "prioridad": "media"},
    {"id": "CT-04", "discrepancia": "Constantes de corrección de temperatura sin origen",
     "evidencia": f"mismas 3 constantes en las 5 hojas: {len({tuple(v) for v in temperatura.values()}) == 1}", "prioridad": "baja"},
    {"id": "CT-02", "discrepancia": "BS&W rotulado «%» y usado como fracción",
     "evidencia": f"rótulos {sorted({h['bsw_unidad_rotulo'] for h in hojas})}; números {min(h['bsw_numero'] for h in hojas):.4f}–{max(h['bsw_numero'] for h in hojas):.4f}",
     "prioridad": "media"},
])
T(discrepancias, ancha=True)
"""),
        M(r"""
La columna **prioridad** es una estimación basada en el efecto sobre el resultado que se mide en el cuaderno 05 (alta: mueve el caudal calculado más que la propia diferencia calculado-medido; media: lo mueve poco pero cambia la interpretación física; baja: efecto menor). No sustituye la decisión del responsable técnico.
"""),
        M(r"""
## Paso 7 · Catálogo de fórmulas y decisión de uso

El catálogo común clasifica cada fórmula según lo que **se puede afirmar con evidencia hoy**. «Utilizable con reserva» significa: se transcribe, reproduce la hoja, y hay una consulta abierta que puede cambiar su sentido. Ninguna fórmula está aprobada para uso operativo: la puerta de fórmulas del plan no se da por satisfecha.
"""),
        C(r"""
from analisis.catalogo_bes_jun import ESTADOS_VALIDOS, FORMULAS
catalogo = pd.DataFrame(FORMULAS)
T(catalogo[["id", "celda", "estado", "consulta"]].rename(columns={"celda": "celda(s) de la hoja", "consulta": "reservas"}))
"""),
        C(r"""
T(catalogo[["id", "aplica", "en_excel"]].rename(columns={"aplica": "qué se transcribe", "en_excel": "lo que dice el libro"}), ancha=True)
"""),
        M(r"""
## Paso 8 · Criterios de aceptación
"""),
        C(r"""
import re
consultas = (RAIZ / "docs" / "consultas_tecnicas_pendientes.md").read_text(encoding="utf-8")
ids_existentes = set(re.findall(r"\| (CT-\d+) \|", consultas))
referidas = {c.strip() for texto in catalogo["consulta"] for c in texto.split(",") if c.strip()}
crit = Criterios("02_trazabilidad_y_analisis_formulas")
crit.comprobar("C02-1", "Las 9 fórmulas tienen firma idéntica en las 5 hojas", bool(firmas_tabla["idéntica en 5 hojas"].all()),
               f"{len(firmas_tabla)} celdas × {len(celdas)} hojas")
crit.comprobar("C02-2", "Toda constante literal está clasificada", int((constantes["estado"] == "SIN CLASIFICAR").sum()) == 0,
               f"{len(constantes)} constantes")
crit.comprobar("C02-3", "Exponente de fricción igual en las 5 hojas y distinto del PDF (registrado)",
               len({tuple(v) for v in exponentes.values()}) == 1 and exponentes["QF-554H"] == [4.8566],
               f"hoja {exponentes['QF-554H']} vs PDF [4.8655]")
crit.comprobar("C02-4", "Consistencia hidrostática de PIP evaluada y registrada en 5 hojas", len(hidro) == 5 and bool(hidro["sensor más profundo"].all()),
               f"PIP > P sensor en {int(hidro['PIP de la hoja > P sensor'].sum())} hojas → CT-03")
crit.comprobar("C02-5", "Estados válidos y cada reserva remite a una consulta existente",
               set(catalogo["estado"]) <= ESTADOS_VALIDOS and referidas <= ids_existentes,
               f"referidas={sorted(referidas)}; existentes={sorted(ids_existentes)}")
T(crit.tabla())
"""),
        C(r"""
wf.close()
crit.exigir()
print("Todos los criterios de aceptación del cuaderno 02 se cumplen.")
"""),
        M(r"""
## Conclusión técnica

- **Resultado:** las nueve fórmulas de la cadena son idénticas en estructura en las cinco hojas, y quedaron localizadas, leídas en lenguaje de rótulos, con sus constantes clasificadas y sus reservas enlazadas a consultas.
- **Hallazgo principal:** el signo de la corrección de PIP produce, en las cinco hojas, una presión en el intake mayor que la del sensor aunque el intake esté más somero. Es **incompatible con la hidrostática simple** y es la reserva más importante del expediente (CT-03).
- **Reservas secundarias:** exponente de Hazen-Williams distinto del PDF (CT-05) y con aplicabilidad no verificada a este fluido; constantes de temperatura sin origen (CT-04); BS&W rotulado en % (CT-02).
- **Lo que no se hizo:** no se cambió ningún signo, exponente ni constante. Transcribir lo que dice la hoja y **señalar** lo dudoso es la conducta correcta cuando no hay una fuente que dirima.
- **Siguiente paso:** cuaderno 03 (mapeo de variables) y cuaderno 04 (ejecución y verificación de la cadena).
"""),
    ]


if __name__ == "__main__":
    print(guardar(NOMBRE, construir()))
