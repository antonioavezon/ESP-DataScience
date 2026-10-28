"""Cuaderno 04: cálculos determinísticos."""

from informes.cuadernos.base import C, M, PREPARACION, guardar

NOMBRE = "04_calculos_deterministicos"


def construir():
    return [
        M(r"""
# Cuaderno 04 · Cálculos determinísticos

**Expediente:** BES-jun · **Cuaderno:** 5 de 7 · **Estado del expediente:** Listo para revisión (no Completo)

## 1. Introducción y contexto (el problema)
La hoja calcula, en celdas encadenadas, el gradiente del fluido, la presión de admisión (PIP), la altura dinámica que debe vencer la bomba (THD) y el caudal al que la bomba la vence. Esos números se usan para decidir si un pozo opera bien. Un error de transcripción a código —un signo, una constante, una interpolación mal replicada— produce cifras verosímiles y falsas, y nadie lo notaría revisando solo el resultado final.

## 2. Justificación y necesidad
Un cálculo en código que (a) reproduzca **cada paso intermedio** de la hoja, no solo el resultado final, (b) **se niegue a devolver un número** cuando falta una entrada o el caso queda fuera de dominio, (c) entregue cada resultado con su unidad, su fórmula de origen y sus advertencias, y (d) deje claro **qué tipo de resultado es** y para qué sirve y para qué **no**.

## 3. Objetivo general
Transcribir la cadena de cálculo de BES-jun en funciones auditables, demostrar que reproduce las celdas intermedias de las cinco hojas, probar sus casos límite y emitir una ficha de confiabilidad por resultado.

## 4. Dominio y alcance
**Incluye:** gravedad a 60 °F y a temperatura, densidad, gradiente, PIP, THP, fricción, THD y caudal a producir (intersección con la curva de bomba a la velocidad actual), en las cinco hojas; nueve casos límite; ficha de confiabilidad; CSV de resultados.

**No incluye:** cambiar signos, exponentes o constantes (CT-03, CT-04, CT-05); el bloque de potencia, motor y cable (sin origen documentado de sus constantes); predicción; un motor general para otros libros.

## 5. Fuentes y datos (entradas y salidas)
**Entradas:** lector `ingesta.leer_bes_jun`, funciones de `src/modelo_deterministico/`. **Salidas:** `data_procesados/resultados_deterministicos.csv`, tablas de contraste y casos límite, ficha de confiabilidad.

## 6. Objetivos específicos y criterios de aceptación
**C04-1** las 45 comparaciones (9 magnitudes × 5 hojas) coinciden con la hoja con error relativo < 1e-9 · **C04-2** los 9 casos límite (ocho de rechazo y uno de advertencia) se comportan como se espera · **C04-3** las cinco hojas son «calculable» en las tres etapas · **C04-4** cada resultado principal lleva unidad y fórmula de origen · **C04-5** el CSV releído coincide · **C04-6** el libro no cambió.

## 7. Riesgo si este paso falla
Un PIP o un caudal de apariencia razonable pero distinto del de la hoja, o un cálculo que devuelve número con datos incompletos. En un contexto de operación, un valor así puede interpretarse como evidencia de que el pozo está sano o enfermo sin base real.
"""),
        M(r"""
## Preparación del entorno
Misma celda que en los demás cuadernos. Se lee el libro y se toma la huella inicial.
"""),
        C(PREPARACION),
        C(r"""
from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO, leer_libro
from ingesta.mapeo import mapear
sha_inicial = huellas(COPIA_TRABAJO)["sha256"]
hojas = leer_libro()
largo = pd.DataFrame(mapear())
cache = {(f.hoja, f.variable): f.valor for f in largo.itertuples()}   # lo que Excel guardó para cada celda
"""),
        M(r"""
## Paso 1 · El contrato de las funciones

**Principio de diseño.** Cada paso de la cadena es una **función pura** (mismas entradas, misma salida; sin leer archivos ni guardar estado) con un docstring que cita la celda de la hoja que transcribe. Eso permite probarlas una a una y leerlas contra la hoja. Las funciones que combinan etapas (`evaluar_fluido`, `evaluar_balance`, `caudal_a_producir`) devuelven un objeto `Resultado` con **estado** (`calculable` o `no_calculable`), **motivo**, **entradas con unidad**, **resultados con unidad y fórmula** y **advertencias**.
"""),
        C(r"""
import inspect
from modelo_deterministico import fluidos_bes_jun as fl, balance_bes_jun as ba, interseccion_bes_jun as it
funciones = [fl.gravedad_especifica_api, fl.gravedad_oil_a_temperatura, fl.densidad_lb_por_galon, fl.gradiente_psi_por_ft,
             ba.pip_en_ft, ba.thp_en_ft, ba.friccion_hazen_williams_ft, ba.thd_total_ft, it.caudal_a_producir]
T(pd.DataFrame([{"función": f.__name__, "firma": str(inspect.signature(f)).replace("float | None", "float?"),
                 "qué transcribe (primera línea del docstring)": (f.__doc__ or "").strip().splitlines()[0]}
                for f in funciones]), ancha=True)
"""),
        M(r"""
## Paso 2 · Un pozo, paso a paso: QF-554H

Antes de correr las cinco hojas conviene **ver** la cadena completa en una. Cada línea llama a una función y su resultado alimenta la siguiente. La tabla compara cada paso con la **celda de la hoja** donde Excel guardó el mismo concepto; la diferencia absoluta debe ser del orden del error de redondeo de punto flotante (≈ 1e-12 o menos), no de «parecido».
"""),
        C(r"""
h = hojas[0]                                              # QF-554H
sg60 = fl.gravedad_especifica_api(h["api_deg"])                                        # B96
sgT  = fl.gravedad_oil_a_temperatura(sg60, h["temperatura_c"])                         # B98
rho  = fl.densidad_lb_por_galon(h["bsw_numero"], h["densidad_agua_lb_gal"], sgT)       # B100
grad = fl.gradiente_psi_por_ft(rho)                                                    # B102
pip  = ba.pip_en_ft(h["presion_sensor_psi"], h["tvd_intake_ft"], h["tvd_sensor_ft"], grad)   # G96
thp  = ba.thp_en_ft(h["thp_psi"], grad)                                                # G98
fric = ba.friccion_hazen_williams_ft(h["caudal_operacion_bfpd"], h["id_tubing_in"], h["tvd_descarga_ft"])  # G100
thd  = ba.thd_total_ft(h["tvd_descarga_ft"], fric, thp, pip)                           # G102
q = it.caudal_a_producir(thd, h["curva"], h["frecuencia_hz"], h["frecuencia_curva_hz"], h["etapas"])
q_prod = q.resultados["caudal_a_producir_bfpd"]["valor"]                               # B106

pasos = [("Gravedad a 60 °F", "adim.", sg60, "cache_sg_60"), ("Gravedad a T de fondo", "adim.", sgT, "cache_sg_temperatura"),
         ("Densidad del fluido", "lb/gal", rho, "cache_densidad_lb_gal"), ("Gradiente", "psi/ft", grad, "cache_gradiente_psi_ft"),
         ("PIP", "ft", pip, "cache_pip_ft"), ("THP", "ft", thp, "cache_thp_ft"), ("Fricción", "ft", fric, "cache_friccion_ft"),
         ("THD total", "ft", thd, "cache_thd_ft"), ("Caudal a producir", "BFPD", q_prod, "cache_caudal_producir_bfpd")]
T(pd.DataFrame([{"paso": n, "unidad": u, "calculado en Python": v, "guardado en la hoja": cache[("QF-554H", k)],
                 "|diferencia|": abs(v - cache[("QF-554H", k)])} for n, u, v, k in pasos]))
"""),
        M(r"""
**Cómo leer el resultado.** Las nueve magnitudes coinciden con la hoja hasta el redondeo de máquina. Que los **intermedios** coincidan —no solo el resultado final— es lo que descarta que dos errores se compensen. Nótese el origen de cada entrada: el PIP en pies se obtiene de la presión **medida por el sensor** corregida por profundidad; no es una estimación independiente del sensor. La THD lo hereda.
"""),
        M(r"""
## Paso 3 · Las cinco hojas con las funciones de contrato

Ahora se usan las funciones que validan entradas y devuelven `Resultado` (en lugar de las funciones elementales), sobre las **cinco hojas**, y se compara con la caché de cada hoja. Si cualquier hoja resultara `no_calculable`, la comparación fallaría y el criterio C04-3 lo detectaría.
"""),
        C(r"""
from modelo_deterministico.fluidos_bes_jun import evaluar_fluido
from modelo_deterministico.balance_bes_jun import evaluar_balance
from modelo_deterministico.interseccion_bes_jun import caudal_a_producir

MAGNITUDES = [("Gravedad a 60 °F", "adim.", "fl", "sg_60", "cache_sg_60"), ("Gravedad a T de fondo", "adim.", "fl", "sg_temperatura", "cache_sg_temperatura"),
              ("Densidad", "lb/gal", "fl", "densidad_lb_gal", "cache_densidad_lb_gal"), ("Gradiente", "psi/ft", "fl", "gradiente_psi_ft", "cache_gradiente_psi_ft"),
              ("PIP", "ft", "ba", "pip_ft", "cache_pip_ft"), ("THP", "ft", "ba", "thp_ft", "cache_thp_ft"),
              ("Fricción", "ft", "ba", "friccion_ft", "cache_friccion_ft"), ("THD total", "ft", "ba", "thd_total_ft", "cache_thd_ft"),
              ("Caudal a producir", "BFPD", "q", "caudal_a_producir_bfpd", "cache_caudal_producir_bfpd")]
resultados, estados, filas = {}, [], []
for h in hojas:
    rf = evaluar_fluido(h["api_deg"], h["temperatura_c"], h["bsw_numero"], h["densidad_agua_lb_gal"])
    rb = evaluar_balance(h["presion_sensor_psi"], h["thp_psi"], h["tvd_intake_ft"], h["tvd_sensor_ft"], h["tvd_descarga_ft"],
                         rf.resultados["gradiente_psi_ft"]["valor"], h["caudal_operacion_bfpd"], h["id_tubing_in"])
    rq = caudal_a_producir(rb.resultados["thd_total_ft"]["valor"], h["curva"], h["frecuencia_hz"], h["frecuencia_curva_hz"], h["etapas"])
    resultados[h["hoja"]] = {"fl": rf, "ba": rb, "q": rq}
    estados.append({"hoja": h["hoja"], "fluido": rf.estado, "balance": rb.estado, "intersección": rq.estado})
    for nombre, unidad, etapa, clave, k_cache in MAGNITUDES:
        calc = resultados[h["hoja"]][etapa].resultados[clave]["valor"]
        hoja_v = cache[(h["hoja"], k_cache)]
        filas.append({"hoja": h["hoja"], "magnitud": nombre, "unidad": unidad, "calculado": calc, "hoja_excel": hoja_v,
                      "dif_abs": abs(calc - hoja_v), "dif_rel": abs(calc - hoja_v) / abs(hoja_v)})
contraste = pd.DataFrame(filas)
T(pd.DataFrame(estados))
"""),
        C(r"""
resumen = contraste.groupby("magnitud", sort=False).agg(unidad=("unidad", "first"), máx_dif_abs=("dif_abs", "max"), máx_dif_rel=("dif_rel", "max")).reset_index()
print("Comparaciones:", len(contraste), "| mayor diferencia relativa:", f"{contraste['dif_rel'].max():.2e}")
T(resumen)
"""),
        C(r"""
res = pd.DataFrame([{"hoja": h["hoja"], "pozo": h["pozo"], "gradiente (psi/ft)": resultados[h["hoja"]]["fl"].resultados["gradiente_psi_ft"]["valor"],
                     "PIP (ft)": resultados[h["hoja"]]["ba"].resultados["pip_ft"]["valor"], "THP (ft)": resultados[h["hoja"]]["ba"].resultados["thp_ft"]["valor"],
                     "fricción (ft)": resultados[h["hoja"]]["ba"].resultados["friccion_ft"]["valor"], "THD total (ft)": resultados[h["hoja"]]["ba"].resultados["thd_total_ft"]["valor"],
                     "Q a producir (BFPD)": resultados[h["hoja"]]["q"].resultados["caudal_a_producir_bfpd"]["valor"],
                     "Q medido (BFPD)": h["caudal_operacion_bfpd"]} for h in hojas])
T(res, ancha=True)
"""),
        M(r"""
**Interpretación.** Las cinco hojas son `calculable` en las tres etapas y las 45 comparaciones coinciden con la hoja con diferencias relativas del orden de **1e-15 o menos** (ruido de punto flotante: Excel y Python suman en orden distinto). Es el máximo respaldo que se puede dar: el código **reproduce la hoja**. No dice que la hoja esté bien. Esa distinción se mantiene en toda la ficha de confiabilidad del Paso 6.

La tabla de resultados resume lo que sigue: gradientes de 0.433 psi/ft (≈ agua, coherente con BS&W de 0.96–0.98); PIP entre ≈ 1 400 y ≈ 1 900 ft de columna; THD entre ≈ 1 500 y ≈ 2 100 ft; y el **caudal a producir** calculado frente al medido, que se evalúa en el cuaderno 05.
"""),
        M(r"""
## Paso 4 · Qué devuelve el código además del número

Un número sin su contexto es peligroso: no dice de qué unidad es, de dónde viene ni qué hay que tener presente al usarlo. Esta celda muestra el `Resultado` completo del balance de una hoja. Obsérvense las **advertencias**: viajan con el número, de modo que quien lo consuma no pueda ignorarlas sin verlas.
"""),
        C(r"""
import json
rb = resultados["QF-554H"]["ba"]
print("estado:", rb.estado)
print("motivo:", rb.motivo)
print("resultados:")
print(json.dumps(rb.resultados, ensure_ascii=False, indent=2))
print("advertencias:")
for a in rb.advertencias + resultados["QF-554H"]["q"].advertencias:
    print(" -", a)
"""),
        M(r"""
## Paso 5 · Casos límite: ¿se niega el código a inventar un número?

**Principio.** Un cálculo correcto con datos buenos es lo mínimo. Lo que distingue software de ingeniería es lo que hace con datos **malos**: si una entrada falta o está fuera de dominio, debe declararse `no_calculable` con un motivo, **no** devolver un número. Se provocan ocho casos sobre la hoja QF-554H y se comprueba el comportamiento esperado. Un caso adicional (BS&W entero) sí calcula, pero debe **advertir**.
"""),
        C(r"""
h = hojas[0]
g0 = resultados["QF-554H"]["fl"].resultados["gradiente_psi_ft"]["valor"]
thd0 = resultados["QF-554H"]["ba"].resultados["thd_total_ft"]["valor"]
bal = lambda **kw: evaluar_balance(**{"presion_sensor_psi": h["presion_sensor_psi"], "thp_psi": h["thp_psi"], "tvd_intake_ft": h["tvd_intake_ft"],
        "tvd_sensor_ft": h["tvd_sensor_ft"], "tvd_descarga_ft": h["tvd_descarga_ft"], "gradiente_psi_ft": g0,
        "caudal_bfpd": h["caudal_operacion_bfpd"], "id_tubing_in": h["id_tubing_in"], **kw})
inter = lambda thd=thd0, **kw: caudal_a_producir(thd, h["curva"], **{"frecuencia_hz": h["frecuencia_hz"], "frecuencia_curva_hz": h["frecuencia_curva_hz"], "etapas": h["etapas"], **kw})
casos = [
    ("1. Sin presión de sensor", lambda: bal(presion_sensor_psi=None), "no_calculable", "dato_faltante"),
    ("2. °API = −131.5 (divide por cero)", lambda: evaluar_fluido(-131.5, h["temperatura_c"], h["bsw_numero"], h["densidad_agua_lb_gal"]), "no_calculable", "fuera_de_dominio"),
    ("3. ID del tubing = 0", lambda: bal(id_tubing_in=0.0), "no_calculable", "fuera_de_dominio"),
    ("4. Caudal negativo", lambda: bal(caudal_bfpd=-10.0), "no_calculable", "fuera_de_dominio"),
    ("5. THD mayor que el head de la bomba", lambda: inter(thd=1e9), "no_calculable", "fuera_de_curva_superior"),
    ("6. THD por debajo del último punto de la curva", lambda: inter(thd=-1.0), "no_calculable", "fuera_de_curva_inferior"),
    ("7. Frecuencia de operación = 0", lambda: inter(frecuencia_hz=0.0), "no_calculable", "fuera_de_dominio"),
    ("8. Sin tabla de bomba", lambda: caudal_a_producir(thd0, [], h["frecuencia_hz"], h["frecuencia_curva_hz"], h["etapas"]), "no_calculable", "dato_faltante"),
    ("9. BS&W escrito como 97.55 (porcentaje)", lambda: evaluar_fluido(h["api_deg"], h["temperatura_c"], 97.55, h["densidad_agua_lb_gal"]), "calculable", None),
]
filas = []
for nombre, f, estado_esp, alerta_esp in casos:
    r = f()
    cumple = r.estado == estado_esp and (alerta_esp is None or alerta_esp in r.alertas)
    if alerta_esp is None:
        cumple = cumple and any("fuera de 0 a 1" in a for a in r.advertencias)
    filas.append({"caso": nombre, "esperado": estado_esp + (f" ({alerta_esp})" if alerta_esp else " con advertencia de BS&W"),
                  "obtenido": r.estado + (f" ({', '.join(r.alertas)})" if r.alertas else ""), "cumple": cumple, "motivo / advertencia": r.motivo if r.estado == "no_calculable" else r.advertencias[0]})
casos_df = pd.DataFrame(filas)
T(casos_df, ancha=True)
"""),
        M(r"""
**Interpretación.** Los ocho primeros casos se declaran `no_calculable` con el motivo preciso: **el código no devuelve un número que no pueda sostener**. Los casos 5 y 6 reproducen lo que en la hoja serían `#N/A` y `#REF!` (que Excel muestra pero que el resto de las celdas arrastran); aquí quedan como estado explícito. El caso 9 es el más instructivo: un BS&W escrito como porcentaje **sí se calcula** (la fórmula no tiene cómo saberlo) pero produce un gradiente físicamente imposible; por eso el código advierte y el control `D-06` del cuaderno 01 lo detectaría antes. Defensa en dos capas: detectar en la entrada y advertir en la salida.
"""),
        M(r"""
## Paso 6 · Ficha de confiabilidad por resultado

**Por qué existe.** El cálculo reproduce la hoja; eso es distinto de que el resultado sea confiable para decidir. La ficha hace explícita la diferencia para **cada resultado**: de qué tipo es, si existe una referencia independiente, de qué entradas depende, qué reservas lo afectan y para qué se puede —y para qué **no**— usar.
"""),
        C(r"""
ficha = pd.DataFrame([
    {"resultado": "Gradiente (psi/ft)", "tipo": "cálculo directo de la hoja", "referencia independiente": "no",
     "depende de": "°API, T, BS&W, densidad del agua (parámetros, no medidos por pozo)", "reservas": "CT-02, CT-04; parámetros idénticos en 5 pozos",
     "uso permitido": "reproducir la hoja; análisis de sensibilidad", "uso NO permitido": "decisión operativa"},
    {"resultado": "PIP (ft)", "tipo": "cálculo directo desde la presión del sensor", "referencia independiente": "no (el sensor es la entrada)",
     "depende de": "P sensor (medida), TVD (survey), gradiente", "reservas": "CT-03 (alta): signo opuesto a la hidrostática",
     "uso permitido": "reproducir la hoja", "uso NO permitido": "estimar la presión real de admisión; decisión operativa"},
    {"resultado": "THP (ft)", "tipo": "cálculo directo", "referencia independiente": "no",
     "depende de": "THP (medida), gradiente", "reservas": "hereda las del gradiente", "uso permitido": "reproducir la hoja", "uso NO permitido": "decisión operativa"},
    {"resultado": "Fricción (ft)", "tipo": "cálculo directo (Hazen-Williams)", "referencia independiente": "no",
     "depende de": "Q medido, ID, TVD de descarga como longitud, C = 120", "reservas": "CT-05: exponente y aplicabilidad al fluido",
     "uso permitido": "reproducir la hoja", "uso NO permitido": "dimensionar tubería o decidir"},
    {"resultado": "THD total (ft)", "tipo": "cálculo directo de la hoja", "referencia independiente": "no",
     "depende de": "TVD descarga, fricción, THP, PIP", "reservas": "CT-03, CT-05 (hereda)", "uso permitido": "reproducir la hoja",
     "uso NO permitido": "decidir ajustes de frecuencia o de operación"},
    {"resultado": "Caudal a producir (BFPD)", "tipo": "cálculo directo de la hoja (intersección en tabla de 6 puntos)", "referencia independiente": "parcial: se contrasta con el caudal medido (cuaderno 05)",
     "depende de": "THD, tabla de bomba a 60 Hz, leyes de afinidad, etapas", "reservas": "CT-03, CT-08, CT-09", "uso permitido": "contrastar con el caudal medido, describir la diferencia",
     "uso NO permitido": "afirmar que el pozo «pierde» o «gana» producción"},
])
T(ficha, ancha=True)
"""),
        M(r"""
**Cómo usar la ficha.** La columna «uso NO permitido» es una **barrera**, no una formalidad: cierra el paso entre «el código dio X» y «hagamos Y». Hasta que se resuelvan las consultas que figuran en «reservas» y exista una referencia independiente, ningún resultado de este cuaderno debe llevarse a una decisión operativa.
"""),
        M(r"""
## Paso 7 · Guardar los resultados y verificarlos
"""),
        C(r"""
import numpy as np
salida = []
for h in hojas:
    fila = {"hoja": h["hoja"], "pozo": h["pozo"]}
    for nombre, unidad, etapa, clave, k_cache in MAGNITUDES:
        v = resultados[h["hoja"]][etapa].resultados[clave]["valor"]
        fila[f"{clave}"] = v
        fila[f"{clave}__hoja"] = cache[(h["hoja"], k_cache)]
    fila["caudal_medido_bfpd"] = h["caudal_operacion_bfpd"]
    salida.append(fila)
salida = pd.DataFrame(salida)
ruta = RAIZ / "data_procesados" / "resultados_deterministicos.csv"
salida.to_csv(ruta, index=False)
rel = pd.read_csv(ruta)
csv_ok = rel.shape == salida.shape and np.allclose(rel.select_dtypes("number").to_numpy(), salida.select_dtypes("number").to_numpy(), rtol=1e-12, atol=0)
print("Escrito:", ruta.relative_to(RAIZ), "| filas:", len(rel), "| columnas:", rel.shape[1], "| relectura idéntica:", "SÍ" if csv_ok else "NO")
"""),
        M(r"""
## Paso 8 · Criterios de aceptación
"""),
        C(r"""
crit = Criterios("04_calculos_deterministicos")
crit.comprobar("C04-1", "45 comparaciones con error relativo < 1e-9", len(contraste) == 45 and bool((contraste["dif_rel"] < 1e-9).all()),
               f"mayor error relativo = {contraste['dif_rel'].max():.2e}")
crit.comprobar("C04-2", "Los 9 casos límite se comportan como se espera", bool(casos_df["cumple"].all()), f"{int(casos_df['cumple'].sum())}/{len(casos_df)}")
crit.comprobar("C04-3", "Las 5 hojas son «calculable» en las tres etapas", all(e[k] == "calculable" for e in estados for k in ("fluido", "balance", "intersección")), "15/15")
principales = [("fl", ["sg_60", "sg_temperatura", "densidad_lb_gal", "gradiente_psi_ft"]), ("ba", ["pip_ft", "thp_ft", "friccion_ft", "thd_total_ft"]), ("q", ["caudal_a_producir_bfpd"])]
completos = all("unidad" in resultados[h["hoja"]][e].resultados[k] and "formula" in resultados[h["hoja"]][e].resultados[k] for h in hojas for e, claves in principales for k in claves)
crit.comprobar("C04-4", "Cada resultado principal lleva unidad y fórmula de origen", completos, "9 resultados × 5 hojas")
crit.comprobar("C04-5", "CSV releído coincide", csv_ok, ruta.name)
crit.comprobar("C04-6", "El libro no cambió", huellas(COPIA_TRABAJO)["sha256"] == sha_inicial, sha_inicial[:16] + "…")
T(crit.tabla())
"""),
        C(r"""
crit.exigir()
print("Todos los criterios de aceptación del cuaderno 04 se cumplen.")
"""),
        M(r"""
## Conclusión técnica

- **Resultado:** la cadena de cálculo de BES-jun —desde °API hasta el caudal a producir— está transcrita en funciones auditables que reproducen **todas** las celdas intermedias de las cinco hojas, y se niega a calcular cuando faltan datos o el caso es inválido.
- **Qué se puede afirmar:** el código y la hoja calculan **lo mismo**. Es una reproducción, no una validación.
- **Qué NO se puede afirmar:** que el PIP sea la presión real de admisión (CT-03), que la fricción sea la de este fluido (CT-05), ni que los parámetros de fluido sean propios de cada pozo (cuaderno 03). La ficha de confiabilidad prohíbe expresamente llevar estos resultados a una decisión operativa.
- **Calidad de ingeniería lograda:** pruebas automáticas (`pytest`: 35), casos límite ejecutados, advertencias que viajan con el número, criterios de aceptación que detienen la ejecución.
- **Siguiente paso:** cuaderno 05, evaluación por pozo y sensibilidad a las ambigüedades.
"""),
    ]


if __name__ == "__main__":
    print(guardar(NOMBRE, construir()))
