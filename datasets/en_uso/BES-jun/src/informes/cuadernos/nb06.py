"""Cuaderno 06: hallazgos y reglas candidatas."""

from informes.cuadernos.base import C, M, PREPARACION, guardar

NOMBRE = "06_hallazgos_y_reglas_candidatas"


def construir():
    return [
        M(r"""
# Cuaderno 06 · Hallazgos y reglas candidatas

**Expediente:** BES-jun · **Cuaderno:** 7 de 7 · **Estado del expediente:** Listo para revisión (no Completo)

## 1. Introducción y contexto (el problema)
Seis cuadernos de análisis producen decenas de observaciones. Si quedan dispersas, tres cosas se pierden: la **prioridad** (¿qué hay que resolver primero?), la **trazabilidad** (¿de dónde sale cada afirmación?) y la **frontera** entre lo que los datos permiten afirmar y lo que no. Además, una «regla» formulada con prisa convierte una observación en una instrucción de operación, que es justo lo que este expediente no puede hacer todavía.

## 2. Justificación y necesidad
Un registro único de hallazgos, **calculados desde la evidencia** (no escritos a mano), cada uno con su efecto sobre el cálculo, su consulta técnica asociada y su prioridad; la especificación completa de las reglas candidatas, ejecutadas sobre las cinco hojas; y una declaración explícita de lo que se puede y lo que no se puede afirmar.

## 3. Objetivo general
Consolidar los hallazgos de los cuadernos 00–05, enlazar cada uno con una consulta técnica (CT) y con una regla o decisión, ejecutar las reglas candidatas y establecer los límites de afirmación del expediente.

## 4. Dominio y alcance
**Incluye:** registro de 13 hallazgos con evidencia recalculada; matriz hallazgo → consulta; especificación y ejecución de `RC-BES-01` a `RC-BES-04`; tabla de afirmaciones permitidas y no permitidas.

**No incluye:** aprobar reglas, definir umbrales de operación, proponer cambios de frecuencia, usar un modelo de lenguaje, ni mezclar con otros datasets. Todo queda **pendiente de revisión humana**.

## 5. Fuentes y datos (entradas y salidas)
**Entradas:** las cinco hojas, las funciones de contrato, el módulo de reglas y `docs/consultas_tecnicas_pendientes.md`. **Salidas:** tablas de hallazgos y de reglas, matriz de consultas y dictamen de afirmaciones.

## 6. Objetivos específicos y criterios de aceptación
**C06-1** cada hallazgo tiene evidencia no vacía y una consulta o un motivo para no tenerla · **C06-2** las consultas CT-01…CT-10 del registro están cubiertas por al menos un hallazgo y viceversa · **C06-3** las reglas dan 5 `RC-BES-03` y ninguna `RC-BES-01` ni `RC-BES-02` en la misma base de frecuencia · **C06-4** todas las reglas están en estado `pendiente` · **C06-5** `RC-BES-04` queda declarada no evaluable · **C06-6** el libro no cambió.

## 7. Riesgo si este paso falla
Que un lector tome una hipótesis como hecho, una regla candidata como norma, o pierda de vista que el signo de una corrección (CT-03) pesa más que todas las constantes juntas. En un entorno donde un caudal mal interpretado puede llevar a modificar la operación de un pozo, la diferencia entre «observación» y «decisión» es una barrera de seguridad.
"""),
        M(r"""
## Preparación del entorno
Se recalcula todo lo necesario desde el libro: el registro de hallazgos **no se escribe a mano**; cada cifra de la columna «evidencia» sale de un cálculo de esta misma ejecución.
"""),
        C(PREPARACION),
        C(r"""
import re
from openpyxl import load_workbook
from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO, leer_libro
from ingesta.estructura_libro import anclas_por_hoja, errores_cacheados
from analisis.dependencias import precedentes
from analisis.cadena import calcular_hoja
from analisis.sensibilidad import tabla_de_impacto, densidad_si_bsw_fuera_de_fraccion
from reglas.candidatas_bes_jun import comparar_caudal_con_limites
sha_inicial = huellas(COPIA_TRABAJO)["sha256"]
hojas = leer_libro()
calc = {h["hoja"]: calcular_hoja(h) for h in hojas}
impacto = pd.DataFrame([f for h in hojas for f in tabla_de_impacto(h)])
print(len(hojas), "hojas;", len(impacto), "escenarios de sensibilidad")
"""),
        M(r"""
## Paso 1 · Reunir la evidencia de cada hallazgo

Cada hallazgo se asocia a un cálculo concreto. Se hace en una celda aparte para que la evidencia quede visible antes de redactar el registro.

- **H-01** comparación sin escalar frente a escalada (cuaderno 05).
- **H-02** hidrostática del signo de PIP (cuaderno 02).
- **H-03** errores `#DIV/0!` y su rastreo (cuaderno 01).
- **H-04…H-13** rótulos, constantes, fechas, tablas repetidas y parámetros idénticos (cuadernos 01–03).
"""),
        C(r"""
ev = {}
# H-01: efecto de comparar sin escalar
sin_escalar = [comparar_caudal_con_limites(h, escalar=False)[0]["id"] for h in hojas]
con_escala = [comparar_caudal_con_limites(h)[0]["id"] for h in hojas]
ev["H-01"] = f"sin escalar: {sin_escalar.count('RC-BES-01')} alerta(s) RC-BES-01; escalado: {con_escala.count('RC-BES-01')}"

# H-02: PIP de la hoja frente a la presión del sensor
mayores = 0
for h in hojas:
    g = calc[h["hoja"]]["fl"].resultados["gradiente_psi_ft"]["valor"]
    mayores += (h["cache_pip_ft"] * g > h["presion_sensor_psi"]) and (h["tvd_sensor_ft"] > h["tvd_intake_ft"])
ev["H-02"] = f"PIP de la hoja > P sensor con el sensor más profundo en {mayores} de {len(hojas)} hojas; ΔQ por signo: {impacto[impacto.consulta=='CT-03'].d_q_bfpd.abs().min():.0f} a {impacto[impacto.consulta=='CT-03'].d_q_bfpd.abs().max():.0f} BFPD"

# H-03: errores #DIV/0! y rastreo de precedentes
errores = pd.DataFrame(errores_cacheados())
wf = load_workbook(COPIA_TRABAJO, data_only=False)
con_error = errores.groupby("hoja")["celda"].apply(set).to_dict()
contaminadas = 0
for a in anclas_por_hoja():
    for celda in (f"G{a['THD TOTAL']}", f"B{a['Caudal a producir']}"):
        p = precedentes(wf[a["hoja"]], celda)
        contaminadas += len((p["formulas"] | p["constantes"]) & con_error.get(a["hoja"], set()))
ev["H-03"] = f"{len(errores)} celdas con error en {errores['hoja'].nunique()} hoja(s) ({', '.join(sorted(errores['hoja'].unique()))}); errores entre precedentes de THD y Q: {contaminadas}"

# H-04: BS&W
bsw = [h["bsw_numero"] for h in hojas]
x100 = [densidad_si_bsw_fuera_de_fraccion(h)["densidad_si_se_usara_x100_lb_gal"] for h in hojas]
ev["H-04"] = f"BS&W {min(bsw):.4f}–{max(bsw):.4f} con rótulo «{hojas[0]['bsw_unidad_rotulo']}»; ×100 daría {min(x100):.0f}–{max(x100):.0f} lb/gal (agua: {hojas[0]['densidad_agua_lb_gal']})"

# H-05 / H-06: constantes y exponente
ev["H-05"] = f"quitar la corrección de temperatura mueve Q hasta {impacto[impacto.consulta=='CT-04'].d_q_bfpd.abs().max():.1f} BFPD"
ev["H-06"] = f"exponente 4.8655 en vez de 4.8566 mueve Q hasta {impacto[impacto.consulta=='CT-05'].d_q_bfpd.abs().max():.1f} BFPD"

# H-07: fechas
hoy = [h["hoja"] for h in hojas if h["fecha_es_today"]]
otras = [(h["hoja"], h["fecha_cache"][:10]) for h in hojas if not h["fecha_es_today"]]
ev["H-07"] = f"{len(hoy)} hojas con =TODAY(); fecha escrita: {otras}"

# H-08: factor 24
f1, f2 = wf["QF-378HST"]["G23"].value, wf["QF-378HST"]["B68"].value
ev["H-08"] = f"QF-378HST!G23 {f1}; QF-378HST!B68 {f2}"

# H-09: tablas de bomba repetidas
grupos = {}
for h in hojas:
    grupos.setdefault(repr([(p['caudal_bfpd'], p['head_ft'], p['brake_hp'], p['eff_numero']) for p in h["curva"]]), []).append(f"{h['hoja']} ({h['bomba_referencia']})")
rep = [g for g in grupos.values() if len(g) > 1]
ev["H-09"] = "; ".join(" = ".join(g) for g in rep) if rep else "sin tablas repetidas"

# H-10: EFF
effmax = max(p["eff_numero"] for h in hojas for p in h["curva"])
ev["H-10"] = f"EFF máx. {effmax} con rótulo «{hojas[0]['curva'][0]['eff_unidad_rotulo']}»"

# H-11: parámetros idénticos
ident = [k for k in ("api_deg", "presion_yacimiento_psi", "presion_burbuja_psi", "densidad_agua_lb_gal") if len({h[k] for h in hojas}) == 1]
ev["H-11"] = "idénticos en 5 hojas: " + ", ".join(f"{k} = {hojas[0][k]}" for k in ident)

# H-12: llave
ev["H-12"] = "cluster = hoja en " + str(sum(h["cluster"] == h["hoja"] for h in hojas)) + " de 5; pozo distinto del nombre de hoja en " + str(sum(h["pozo"] != h["hoja"] for h in hojas))

# H-13: calculado vs medido
dif = [100 * (calc[h["hoja"]]["q"].resultados["caudal_a_producir_bfpd"]["valor"] - h["caudal_operacion_bfpd"]) / calc[h["hoja"]]["q"].resultados["caudal_a_producir_bfpd"]["valor"] for h in hojas]
ev["H-13"] = f"calculado − medido entre {min(dif):.1f} % y {max(dif):+.1f} % (n = 5)"
for k, v in ev.items():
    print(k, "|", v)
"""),
        M(r"""
**Qué muestra esta salida.** Una línea por hallazgo, con la cifra que lo respalda. Nada está escrito a mano: si el libro cambiara, estas líneas cambiarían (y los criterios del final lo detectarían si algo dejara de ser cierto). Ya se puede ver que el hallazgo H-02 (signo de PIP) tiene un efecto cuantificado sobre el caudal, mientras que H-05 y H-06 son efectos de segundo orden.
"""),
        M(r"""
## Paso 2 · Registro de hallazgos

Cada hallazgo declara: **qué es** (observación), su **efecto en el cálculo**, la **consulta técnica** que lo cierra y su **prioridad**. La prioridad no es una opinión: sale de dos preguntas, *¿mueve el resultado?* (Paso 1) y *¿se puede resolver con los datos disponibles?* (no).
"""),
        C(r"""
registro = pd.DataFrame([
    ("H-01", "Comparar el caudal con el límite sin escalar mezcla 63 Hz con 60 Hz y genera una alarma falsa", "Alto si se usara: activaría una regla de operación", "CT-08", "Corregido en el código; CT-08 (validez de Q ∝ f) sigue abierta"),
    ("H-02", "La corrección de PIP suma en vez de restar la columna hidrostática (sensor más profundo que el intake)", "Alto: cambia THD y Q", "CT-03", "Alta"),
    ("H-03", "Hay 13 celdas con #DIV/0! en una hoja, lejos de la cadena de cálculo", "Ninguno en el cálculo; defecto del libro", "—", "Informativa (avisar al responsable)"),
    ("H-04", "El BS&W está rotulado «%» pero la fórmula lo usa como fracción", "Ninguno si se respeta; error de lectura posible", "CT-02", "Media"),
    ("H-05", "La corrección de temperatura usa constantes sin origen documentado", "Bajo", "CT-04", "Baja"),
    ("H-06", "El exponente de fricción de la hoja difiere del del PDF", "Bajo a medio", "CT-05", "Media"),
    ("H-07", "Cuatro fechas son =TODAY(); una hoja trae fecha escrita sin explicación", "Impide cualquier eje temporal", "—", "Informativa (limita el alcance)"),
    ("H-08", "Aparece un factor 24 en caudales de una hoja", "Posible diferencia de definición del caudal", "CT-07", "Baja"),
    ("H-09", "Tablas de bomba idénticas repetidas entre pozos", "Curvas posiblemente genéricas, no de cada pozo", "CT-06", "Baja"),
    ("H-10", "La columna EFF se rotula «%» y llega a un máximo muy bajo", "Impide hablar de BEP", "CT-06", "Baja"),
    ("H-11", "°API, presión de yacimiento y de burbuja son idénticos en los cinco pozos", "Posible dato de plantilla que alimenta el gradiente", "CT-10", "Media"),
    ("H-12", "No hay una llave única inequívoca: Cluster coincide con el nombre de la hoja y Pozo es otro identificador", "Ninguno si no se fusiona", "CT-01", "Baja"),
    ("H-13", "El caudal calculado difiere del medido sin tolerancia definida", "Informativo", "CT-09", "Media"),
], columns=["id", "hallazgo", "efecto en el cálculo", "consulta", "prioridad"])
registro["evidencia (recalculada)"] = registro["id"].map(ev)
T(registro, ancha=True)
"""),
        M(r"""
**Interpretación.** De 13 hallazgos, **solo dos** pueden cambiar de verdad un resultado de ingeniería: el que ya se corrigió (H-01, un error de *nuestro* análisis) y H-02, el signo de PIP, que es una ambigüedad **del libro** que no puede resolverse sin el responsable. El resto son riesgos de lectura (H-04, H-10), límites del alcance (H-07, H-11, H-13) o defectos que no tocan el cálculo (H-03). Esta jerarquía es la que debería orientar la conversación con quien mantiene el libro.

Un detalle de método: **H-01 es un error propio** y se incluye en el registro sin atenuarlo. Un expediente que solo registra los errores de los demás pierde credibilidad; este conserva la corrección como prueba permanente (criterio `C05-3`).
"""),
        M(r"""
## Paso 3 · Matriz hallazgo → consulta técnica

Esta matriz comprueba la **cobertura en ambos sentidos**: cada consulta del registro `docs/consultas_tecnicas_pendientes.md` debe nacer de algún hallazgo, y cada hallazgo con consulta debe encontrarse en ese registro. Así ninguna pregunta queda huérfana ni ningún hallazgo sin destino.
"""),
        C(r"""
doc_ct = (RAIZ / "docs" / "consultas_tecnicas_pendientes.md").read_text(encoding="utf-8")
ct_del_doc = sorted(set(re.findall(r"^\| (CT-\d+) \|", doc_ct, flags=re.M)))
ct_de_hallazgos = sorted({c for c in registro["consulta"] if c.startswith("CT-")})
matriz = pd.DataFrame([{"consulta": ct, "hallazgos": ", ".join(registro[registro["consulta"] == ct]["id"]) or "—"} for ct in ct_del_doc])
print("Consultas en el registro:", ct_del_doc)
print("Sin hallazgo:", sorted(set(ct_del_doc) - set(ct_de_hallazgos)), "| hallazgos con consulta inexistente:", sorted(set(ct_de_hallazgos) - set(ct_del_doc)))
T(matriz)
"""),
        M(r"""
**Interpretación.** Las consultas CT-01 a CT-10 aparecen enlazadas con al menos un hallazgo; **CT-08** (validez de las leyes de afinidad) se relaciona con H-01 y es la única consulta cuyo hallazgo es una **dependencia del modelo** y no una anomalía de una celda. Si la tabla mostrara una consulta «—» o la lista «sin hallazgo» no estuviera vacía, el criterio `C06-2` detendría el cuaderno.
"""),
        M(r"""
## Paso 4 · Reglas candidatas: especificación y ejecución

Una regla candidata es una **condición legible, con umbral escrito en la propia hoja, que genera una observación revisable** (no una orden). Cada regla se especifica con todos sus campos (condición, variables, umbral, resultado, explicación, verificación, confianza, estado y limitaciones) y se **ejecuta** sobre las cinco hojas para ver qué diría.
"""),
        C(r"""
T(pd.DataFrame([
    {"id": "RC-BES-01", "condición": "Q operación > límite máximo escrito, a la misma frecuencia (Q_máx · f/60)", "umbral": "celda «Limite maximo» de la hoja", "resultado": "advertencia por_encima_del_limite_maximo", "confianza": "baja", "estado": "pendiente",
     "limitación": "el máximo es un número de la hoja, no de fabricante (CT-06); depende de Q ∝ f (CT-08)"},
    {"id": "RC-BES-02", "condición": "Q operación < límite mínimo escrito, a la misma frecuencia", "umbral": "celda «Limite minimo» de la hoja", "resultado": "advertencia por_debajo_del_limite_minimo", "confianza": "baja", "estado": "pendiente",
     "limitación": "ídem"},
    {"id": "RC-BES-03", "condición": "mínimo ≤ Q operación ≤ máximo, a la misma frecuencia", "umbral": "ambas celdas", "resultado": "dentro_de_los_limites_escritos", "confianza": "baja", "estado": "pendiente",
     "limitación": "no autoriza operar; solo dice que la hoja es coherente consigo misma"},
    {"id": "RC-BES-04", "condición": "cercanía al BEP (punto de máxima eficiencia)", "umbral": "no hay: requiere curva de fabricante", "resultado": "no evaluable", "confianza": "—", "estado": "no evaluable",
     "limitación": "la curva de EFF es una tabla de la hoja sin respaldo de fabricante (CT-06)"},
]), ancha=True)
"""),
        C(r"""
ejecucion = pd.DataFrame([{**comparar_caudal_con_limites(h)[0], "bomba": h["bomba_referencia"]} for h in hojas])
T(ejecucion[["hoja", "pozo", "bomba", "frecuencia_operacion_hz", "caudal_bfpd", "limite_minimo_bfpd", "limite_maximo_bfpd", "uso_del_limite_maximo_pct", "id", "resultado", "estado_revision", "nivel_confianza"]]
  .rename(columns={"frecuencia_operacion_hz": "f (Hz)", "caudal_bfpd": "Q (BFPD)", "limite_minimo_bfpd": "mín @f", "limite_maximo_bfpd": "máx @f", "uso_del_limite_maximo_pct": "uso máx (%)"}), ancha=True)
"""),
        M(r"""
**Interpretación.** Las cinco hojas dan `RC-BES-03`: están dentro de los límites escritos a su frecuencia. **Ninguna regla de advertencia se activa**. Esto no es «todo está bien»: es que **la hoja es coherente consigo misma en este punto**. Lo que sí merece mirarse es el *uso del máximo*: QF-554H está al 98 % de su máximo a 63 Hz; si el máximo escrito fuese un límite real, el margen sería pequeño. Eso es lo que la regla `RC-BES-03` **no** dice, y por eso lleva confianza baja y estado pendiente.

La regla `RC-BES-04` no se ejecuta, y eso es deliberado. A continuación se comprueba **por qué** no es evaluable.
"""),
        C(r"""
filas = []
for h in hojas:
    mejor = max(h["curva"], key=lambda p: p["eff_numero"])
    filas.append({"hoja": h["hoja"], "bomba": h["bomba_referencia"], "«Cono de eficiencia» (BFPD)": h["cono_eficiencia_bfpd"],
                  "Q de mayor EFF tabulada (BFPD)": mejor["caudal_bfpd"], "EFF máx. (rótulo %)": mejor["eff_numero"],
                  "coinciden": h["cono_eficiencia_bfpd"] == mejor["caudal_bfpd"]})
bep = pd.DataFrame(filas)
T(bep, ancha=True)
"""),
        M(r"""
**Interpretación.** El «Cono de eficiencia» coincide con el caudal de mayor EFF de la tabla, pero esa EFF máxima es de apenas unos puntos «%» (una cifra baja para una eficiencia de bomba: en general una ESP en su mejor punto opera con decenas de puntos porcentuales; es conocimiento general, no un dato de las fuentes del expediente). Por tanto **no se sabe qué magnitud representa EFF** en la hoja y **no puede llamarse BEP** a ese caudal. Convertir esto en regla («operar a ±X % del BEP») sería inventar una referencia que el libro no avala. Queda como hallazgo (H-10) y consulta (CT-06).
"""),
        M(r"""
## Paso 5 · Qué se puede y qué no se puede afirmar

La salida más importante del expediente es esta frontera. Se escribe en una tabla para que sea imposible citar una afirmación fuera de su lugar.
"""),
        C(r"""
T(pd.DataFrame([
    ("Las cifras del libro se transcriben sin alteración (ida y vuelta, 170 celdas)", "Sí", "cuaderno 03"),
    ("El código reproduce PIP, THD y Q a producir de las cinco hojas (≤ 1e-15)", "Sí", "cuadernos 04 y 05"),
    ("Las cinco hojas están dentro de los límites escritos a su frecuencia", "Sí, como coherencia interna", "este cuaderno"),
    ("El signo de la corrección de PIP es el correcto", "No: ambigüedad abierta (CT-03)", "cuaderno 02"),
    ("El modelo predice el caudal de un pozo", "No: no evaluable", "cuaderno 05, Paso 6"),
    ("El caudal calculado coincide con el medido", "No se puede decir «coincide»: difiere entre −5.9 % y +8.8 %, sin tolerancia (CT-09)", "cuaderno 05"),
    ("Un pozo está operando mal", "No: ninguna regla está aprobada", "este cuaderno"),
    ("Hay que cambiar la frecuencia de un pozo", "No: fuera del alcance", "—"),
    ("Los límites del libro son de fabricante", "No se sabe (CT-06)", "cuaderno 03"),
    ("Los parámetros de fluido son de cada pozo", "No se sabe: idénticos en cinco pozos", "cuaderno 03"),
], columns=["afirmación", "¿permitida?", "dónde se sustenta"]), ancha=True)
"""),
        M(r"""
## Paso 6 · Criterios de aceptación
"""),
        C(r"""
crit = Criterios("06_hallazgos_y_reglas_candidatas")
crit.comprobar("C06-1", "Cada hallazgo tiene evidencia y consulta o motivo", bool((registro["evidencia (recalculada)"].fillna("").str.len() > 0).all()) and bool((registro["consulta"].str.len() > 0).all()),
               f"{len(registro)} hallazgos")
crit.comprobar("C06-2", "CT del registro cubiertas por hallazgos y viceversa", set(ct_del_doc) == set(ct_de_hallazgos), f"{len(ct_del_doc)} consultas")
ids = list(ejecucion["id"])
crit.comprobar("C06-3", "5 RC-BES-03 y ninguna RC-BES-01/02 en la misma base", ids.count("RC-BES-03") == 5 and ids.count("RC-BES-01") == 0 and ids.count("RC-BES-02") == 0, str(ids))
crit.comprobar("C06-4", "Todas las reglas ejecutadas están pendientes", bool((ejecucion["estado_revision"] == "pendiente").all()), "pendiente")
crit.comprobar("C06-5", "RC-BES-04 no evaluable: tablas repetidas entre pozos y cono = caudal de máxima EFF tabulada", bool(rep) and bool(bep["coinciden"].all()), f"{len(rep)} grupos de tablas repetidas; EFF máx. {effmax} con rótulo %")
crit.comprobar("C06-6", "El libro no cambió", huellas(COPIA_TRABAJO)["sha256"] == sha_inicial, sha_inicial[:16] + "…")
T(crit.tabla())
"""),
        C(r"""
crit.exigir()
print("Todos los criterios de aceptación del cuaderno 06 se cumplen.")
"""),
        M(r"""
## Conclusión técnica

- **Resultado:** 13 hallazgos con evidencia recalculada, cada uno enlazado con su consulta técnica y priorizado; cuatro reglas especificadas, tres ejecutadas (todas en estado pendiente) y una declarada no evaluable.
- **Lo más importante:** la ambigüedad de signo de la corrección de PIP (CT-03) es la que más condiciona el caudal calculado; el resto son efectos menores o límites del alcance. La corrección de la falsa alarma de frecuencia (H-01) es un error propio, registrado como tal.
- **Qué se puede hacer con esto:** llevar a quien mantiene el libro una lista corta y ordenada de diez preguntas, con la cifra que motiva cada una.
- **Qué no:** aprobar reglas, declarar validado el modelo, ni dar una instrucción de operación. Eso exige las respuestas a las consultas y revisión humana.
- **Estado del expediente:** **Listo para revisión**. P-14 sigue pendiente y no se mueve a `procesadas/`.
"""),
    ]


if __name__ == "__main__":
    print(guardar(NOMBRE, construir()))
