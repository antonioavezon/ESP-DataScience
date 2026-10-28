"""Cuaderno 05: evaluación por pozo."""

from informes.cuadernos.base import C, M, PREPARACION, guardar

NOMBRE = "05_evaluacion_por_pozo"


def construir():
    return [
        M(r"""
# Cuaderno 05 · Evaluación por pozo

**Expediente:** BES-jun · **Cuaderno:** 6 de 7 · **Estado del expediente:** Listo para revisión (no Completo)

## 1. Introducción y contexto (el problema)
El cuaderno 04 mostró que el código reproduce la hoja. Reproducir no es evaluar. Para decir algo sobre la calidad del cálculo hay que contrastarlo con algo **distinto de sí mismo**, y hay que saber cuánto valen esas referencias. Presentar como «validación» una comparación contra la caché de Excel, o como «predicción» el ajuste de un único punto por pozo, sería afirmar más de lo que los datos permiten.

## 2. Justificación y necesidad
Un análisis por pozo que separe, con nombre propio, cuatro cosas: la **reproducción** (código contra hoja), el **contraste** calculado contra medido (única referencia distinta del cálculo), la **ventana operativa** del caudal en una base de frecuencia coherente y la **sensibilidad** a las ambigüedades abiertas; y que declare con criterios explícitos si la **capacidad predictiva** es evaluable.

## 3. Objetivo general
Evaluar cada una de las cinco hojas con las referencias disponibles, cuantificar cuánto mueve cada ambigüedad (CT-02 a CT-05) al caudal calculado, y dictaminar con evidencia qué se puede y qué no se puede afirmar.

## 4. Dominio y alcance
**Incluye:** reproducción contra la caché; contraste del caudal a producir con el caudal medido (n = 5); comparación del caudal de operación con los límites de la hoja a la frecuencia de operación, y la demostración de la falsa alarma que produce comparar sin escalar; sensibilidad a signo de PIP, exponente de Hazen-Williams, corrección de temperatura y lectura de BS&W; evaluación de requisitos de predicción; seis figuras.

**No incluye:** ajustar el modelo, elegir el signo, el exponente o las constantes «que mejor cuadren»; predecir otros días o pozos; declarar un pozo «bueno» o «malo»; aprobar reglas.

## 5. Fuentes y datos (entradas y salidas)
**Entradas:** lector, funciones de contrato (cuaderno 04), `reglas.candidatas_bes_jun`, `analisis.sensibilidad`. **Salidas:** tablas por pozo, seis figuras en `reports/figuras/`, dictamen de capacidad predictiva.

## 6. Objetivos específicos y criterios de aceptación
**C05-1** reproducción con error relativo < 1e-9 · **C05-2** contraste calculado-medido disponible en 5 de 5 hojas · **C05-3** en la misma base de frecuencia las 5 hojas están dentro de sus límites y la comparación sin escalar genera exactamente una alerta (artefacto documentado) · **C05-4** el signo de PIP (CT-03) mueve el caudal más que CT-04 y CT-05 en cada hoja · **C05-5** la capacidad predictiva se declara no evaluable con los requisitos incumplidos listados · **C05-6** las seis figuras existen · **C05-7** el libro no cambió.

## 7. Riesgo si este paso falla
Dar por validado un modelo que solo se reproduce a sí mismo, o activar una alarma de operación por una comparación mal planteada (como la de 63 Hz contra un límite a 60 Hz que existió en la primera versión de este análisis). Una falsa alarma erosiona la confianza; una validación falsa oculta un error real.
"""),
        M(r"""
## Preparación del entorno
Misma celda que en los demás cuadernos. Se leen las hojas, se ejecuta la cadena de cada una con `analisis.cadena.calcular_hoja` (las mismas funciones del cuaderno 04) y se guarda la huella del libro.
"""),
        C(PREPARACION),
        C(r"""
import numpy as np
from IPython.display import Image, display
from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO, leer_libro
from ingesta.survey import leer_survey
from ingesta.mapeo import mapear
from analisis.cadena import calcular_hoja
sha_inicial = huellas(COPIA_TRABAJO)["sha256"]
hojas = leer_libro()
estaciones = leer_survey()
calc = {h["hoja"]: calcular_hoja(h) for h in hojas}
cache = {(f.hoja, f.variable): f.valor for f in pd.DataFrame(mapear()).itertuples()}
print({n: (c["fl"].estado, c["ba"].estado, c["q"].estado) for n, c in calc.items()})
"""),
        M(r"""
## Paso 1 · Qué se puede evaluar y contra qué

Antes de calcular métricas hay que decir **qué prueba cada comparación y qué no**. Una métrica sin su referencia correcta induce a leerla como más fuerte de lo que es.
"""),
        C(r"""
T(pd.DataFrame([
    {"evaluación": "A. Reproducción", "se compara": "código vs caché de Excel", "¿referencia independiente?": "no: misma fórmula",
     "qué demuestra": "que la transcripción es fiel", "qué NO demuestra": "que la fórmula sea correcta"},
    {"evaluación": "B. Calculado vs medido", "se compara": "Q a producir vs Q de operación", "¿referencia independiente?": "parcial: Q medido es un dato de campo, pero también entra a la fricción",
     "qué demuestra": "cuánto se aparta el modelo de un dato medido (n = 5)", "qué NO demuestra": "validación: no hay tolerancia definida (CT-09) ni más puntos"},
    {"evaluación": "C. Ventana operativa", "se compara": "Q de operación vs límites escritos, a la misma frecuencia", "¿referencia independiente?": "no: los límites son de la propia hoja",
     "qué demuestra": "coherencia interna de la hoja", "qué NO demuestra": "que los límites sean de fabricante (CT-06)"},
    {"evaluación": "D. Sensibilidad", "se compara": "resultado con la fórmula de la hoja vs con la alternativa", "¿referencia independiente?": "no aplica",
     "qué demuestra": "cuánto pesa cada ambigüedad", "qué NO demuestra": "cuál alternativa es la correcta"},
    {"evaluación": "E. Predicción", "se compara": "—", "¿referencia independiente?": "—",
     "qué demuestra": "se evalúan requisitos (Paso 6)", "qué NO demuestra": "capacidad predictiva alguna"},
]), ancha=True)
"""),
        M(r"""
## Paso 2 · Evaluación A: reproducción contra la caché

Es el control del cuaderno 04 aplicado por pozo: sirve de línea base. Si aquí hubiera diferencias, todo lo que sigue estaría comprometido.
"""),
        C(r"""
claves = [("PIP", "ba", "pip_ft", "cache_pip_ft"), ("THD", "ba", "thd_total_ft", "cache_thd_ft"), ("Q a producir", "q", "caudal_a_producir_bfpd", "cache_caudal_producir_bfpd")]
repro = pd.DataFrame([{"hoja": h["hoja"], **{f"error rel. {n}": abs(calc[h["hoja"]][e].resultados[k]["valor"] - cache[(h["hoja"], c)]) / abs(cache[(h["hoja"], c)])
                                              for n, e, k, c in claves}} for h in hojas])
print("Mayor error relativo de reproducción:", f"{repro.drop(columns='hoja').to_numpy().max():.2e}")
T(repro)
"""),
        M(r"""
**Interpretación.** Los errores son del orden del redondeo de máquina (≤ 1e-15). La línea base es sólida: las diferencias que aparezcan en los pasos siguientes **no se deben a la transcripción**.
"""),
        M(r"""
## Paso 3 · Evaluación B: calculado frente a medido

**Qué se compara.** La hoja calcula el «Caudal a producir» como el caudal al que la bomba (a la velocidad actual) entrega la altura que exige el sistema (THD). Se compara con el **caudal de operación medido**. La propia hoja define la diferencia como `calculado − medido` y el porcentaje como esa diferencia dividida entre el **calculado** (QF-554H!G106 `=B106-B71`, G110 `=G106/B106`). Se reporta esa definición y, para no depender de ella, también la diferencia relativa al medido.

**Cómo leerla.** Es un contraste, no una validación: el caudal medido participa también en la fricción, el PIP parte de la presión del sensor, y no hay tolerancia definida para llamar «aceptable» a una diferencia (CT-09).
"""),
        C(r"""
filas = []
for h in hojas:
    qc, qm = calc[h["hoja"]]["q"].resultados["caudal_a_producir_bfpd"]["valor"], h["caudal_operacion_bfpd"]
    filas.append({"hoja": h["hoja"], "f (Hz)": h["frecuencia_hz"], "etapas": h["etapas"], "Q calculado (BFPD)": qc, "Q medido (BFPD)": qm,
                  "calculado − medido": qc - qm, "% sobre calculado (hoja)": 100 * (qc - qm) / qc, "% sobre medido": 100 * (qc - qm) / qm})
contraste = pd.DataFrame(filas)
T(contraste, ancha=True)
"""),
        C(r"""
p = contraste["% sobre calculado (hoja)"]
T(pd.DataFrame([{"n": len(p), "media con signo (%)": p.mean(), "media de |error| (%)": p.abs().mean(), "máximo |error| (%)": p.abs().max(),
                 "hojas con calculado > medido": int((p > 0).sum()), "hojas con calculado < medido": int((p < 0).sum())}]))
"""),
        C(r"""
from analisis.graficos import guardar_figuras
rutas = guardar_figuras(hojas, estaciones)
display(Image(filename=str(RAIZ / "reports" / "figuras" / "interseccion_sistema_bomba.png")))
"""),
        M(r"""
**Interpretación de la tabla.** El caudal calculado se aparta del medido entre **−5.9 % y +8.8 %** (definición de la hoja); en tres hojas el calculado es mayor y en dos es menor, de modo que **no hay un sesgo sistemático** en una dirección (la media con signo es pequeña frente al error absoluto medio). Con n = 5, pozos con distinta bomba, etapas y frecuencia, estos números **describen** la diferencia; no estiman un error de predicción y no permiten una afirmación estadística.

**Interpretación de la figura.** Cada panel es un pozo. La curva azul es el **head de la bomba a la frecuencia de operación** (decreciente con el caudal); la línea roja horizontal es la **THD** que exige el sistema; la intersección de ambas (línea naranja) es el «caudal a producir» y la línea verde es el caudal **medido**. En QF-545H y QF-500H la naranja queda a la izquierda de la verde (calculado menor); en QF-378HST queda claramente a la derecha; en QF-549HST casi se superponen. La separación visual entre ambas es la diferencia de la tabla. Obsérvese que la curva es una **poligonal de seis puntos**: la interpolación lineal entre puntos distantes (a veces de miles de BFPD) es una aproximación de la curva real, que no se conoce.
"""),
        M(r"""
## Paso 4 · Evaluación C: ventana operativa en la misma base de frecuencia

**El problema que se descubrió.** Los límites de caudal «Limite minimo», «Cono de eficiencia» y «Limite maximo» están escritos en el bloque de la curva a **60 Hz**. La hoja los lleva a otras frecuencias con `Q(f) = Q(60) · f / 60` (por ejemplo `J85 = J88*(I85/I88)`). Las cinco hojas operan entre 56 y 67 Hz. Comparar el caudal de operación con el límite **sin escalar** mezcla dos bases de frecuencia. La primera versión de este análisis lo hizo y generó una alerta en QF-084; se muestra aquí cómo desaparece al comparar correctamente y se deja la comparación defectuosa como demostración.
"""),
        C(r"""
from reglas.candidatas_bes_jun import comparar_caudal_con_limites, limites_a_frecuencia
filas = []
for h in hojas:
    lim = limites_a_frecuencia(h)
    ok = comparar_caudal_con_limites(h)[0]
    mal = comparar_caudal_con_limites(h, escalar=False)[0]
    filas.append({"hoja": h["hoja"], "pozo": h["pozo"], "f (Hz)": h["frecuencia_hz"], "Q operación": h["caudal_operacion_bfpd"],
                  "mín @f": lim["minimo_bfpd"], "máx @f": lim["maximo_bfpd"], "uso del máx @f (%)": ok["uso_del_limite_maximo_pct"],
                  "regla (misma base)": ok["id"], "máx a 60 Hz sin escalar": h["limite_maximo_bfpd"], "regla (sin escalar, defectuosa)": mal["id"]})
ventana = pd.DataFrame(filas)
T(ventana, ancha=True)
"""),
        C(r"""
display(Image(filename=str(RAIZ / "reports" / "figuras" / "caudal_limites_por_hoja.png")))
"""),
        M(r"""
**Interpretación.** En la misma base de frecuencia, las **cinco** hojas quedan dentro de su ventana (regla `RC-BES-03`); la más cercana a su máximo es QF-554H, con 98.1 % del límite máximo a 63 Hz (10 500 BFPD). La comparación sin escalar activa `RC-BES-01` solo en esa hoja, porque 10 301 BFPD supera 10 000 BFPD: es un **artefacto** de comparar 63 Hz contra 60 Hz, no un hallazgo operativo. Esto se corrigió en el código, en las pruebas y en el informe, y queda documentado en `docs/consultas_tecnicas_pendientes.md`.

*En la figura:* las barras son el caudal de operación; los círculos rellenos, los límites a la frecuencia de operación; el círculo hueco, el máximo escrito (60 Hz). En QF-084 el círculo hueco queda **por debajo** de la barra y el relleno por encima: la diferencia entre ambos es lo que cambia el veredicto.

*Límite de la conclusión:* que el caudal esté dentro de la ventana **de la hoja** no significa que esté dentro de la ventana de la bomba real: la hoja no dice si esos límites son de fabricante (CT-06), y que `Q ∝ f` valga para cada bomba es la consulta CT-08.
"""),
        M(r"""
## Paso 5 · Evaluación D: sensibilidad a las ambigüedades abiertas

**Método.** Para cada ambigüedad se recalcula la cadena con la **alternativa** usando las mismas funciones transcritas (sin escribir fórmulas nuevas) y se mide cuánto cambian PIP, THD y el caudal a producir. Las alternativas son: **CT-03** signo opuesto de la corrección de PIP (intercambiando `TVD_intake` y `TVD_sensor` en la fórmula); **CT-05** exponente 4.8655 del PDF en vez de 4.8566; **CT-04** sin corrección de temperatura de la gravedad. **CT-02** (BS&W) se evalúa aparte, con una prueba lógica. El resultado **no dice cuál alternativa es la correcta**: dice cuánto importa decidirlo.
"""),
        C(r"""
from analisis.sensibilidad import tabla_de_impacto, densidad_si_bsw_fuera_de_fraccion
impacto = pd.DataFrame([f for h in hojas for f in tabla_de_impacto(h)])
cols = ["hoja", "consulta", "escenario", "d_pip_ft", "d_thd_ft", "q_hoja_bfpd", "d_q_bfpd"]
T(impacto[cols].rename(columns={"d_pip_ft": "ΔPIP (ft)", "d_thd_ft": "ΔTHD (ft)", "q_hoja_bfpd": "Q hoja (BFPD)", "d_q_bfpd": "ΔQ (BFPD)"}), ancha=True)
"""),
        C(r"""
display(Image(filename=str(RAIZ / "reports" / "figuras" / "impacto_ambiguedades_en_caudal.png")))
"""),
        M(r"""
**Interpretación de la tabla y la figura.**
- **CT-03 (signo de PIP) domina.** Mueve el PIP en 38 a 51 ft, la THD en el mismo valor con signo contrario y el caudal calculado entre **−106 y −456 BFPD**. Esa magnitud es del mismo orden que la diferencia calculado-medido del Paso 3 (84 a 687 BFPD): la ambigüedad es suficientemente grande como para cambiar la lectura del contraste.
- **CT-05 (exponente)** reduce la THD en 2 a 7 ft y mueve el caudal en +10 a +36 BFPD. **CT-04 (temperatura)** mueve el PIP en 1 a 3 ft y el caudal entre −2 y −15 BFPD: es un efecto pequeño.
- El sentido de cada efecto es coherente con la física de las fórmulas: una THD mayor exige más altura a la bomba, y en su curva decreciente eso corresponde a **menos caudal**.

Con esto se ordenan las consultas por urgencia: **primero CT-03**, después CT-05 y CT-04. Es la base de la columna «prioridad» del registro de discrepancias.
"""),
        M(r"""
### ¿Cierra el signo de PIP la brecha calculado-medido?

Es tentador usar el contraste del Paso 3 para elegir el signo «que mejor ajusta». Se calcula el error absoluto con cada signo **para mostrar por qué no debe hacerse**.
"""),
        C(r"""
tab = impacto[impacto["consulta"] == "CT-03"].set_index("hoja")
comp = pd.DataFrame({"hoja": contraste["hoja"],
                     "|error| con signo de la hoja (BFPD)": contraste["calculado − medido"].abs().to_numpy(),
                     "|error| con signo opuesto (BFPD)": (contraste["Q calculado (BFPD)"].to_numpy() + tab.loc[contraste["hoja"], "d_q_bfpd"].to_numpy() - contraste["Q medido (BFPD)"].to_numpy()).__abs__()})
comp["¿mejora con el signo opuesto?"] = comp["|error| con signo opuesto (BFPD)"] < comp["|error| con signo de la hoja (BFPD)"]
print("Hojas donde el signo opuesto reduce el error:", int(comp["¿mejora con el signo opuesto?"].sum()), "de", len(comp))
T(comp, ancha=True)
"""),
        M(r"""
**Interpretación.** El signo opuesto reduce el error en **dos** hojas y lo aumenta en **tres**. La evidencia es **mixta y con n = 5**: no autoriza a elegir un signo. Y aunque lo hiciera, ajustar una convención física al error de un contraste que no es independiente sería **sobreajuste a un resultado**, no una decisión de ingeniería. La decisión corresponde a quien documente la convención del libro (CT-03).

### Prueba lógica de CT-02 (BS&W)
Si el número de BS&W (0.96–0.98) debiera leerse como porcentaje y se multiplicara por 100 dentro de la fórmula, ¿qué densidad resultaría?
"""),
        C(r"""
bsw = pd.DataFrame([densidad_si_bsw_fuera_de_fraccion(h) for h in hojas]).drop(columns=["x100_es_fisicamente_plausible"])
T(bsw.rename(columns={"bsw_celda": "BS&W en la celda", "densidad_como_fraccion_lb_gal": "densidad como fracción (lb/gal)",
                      "densidad_si_se_usara_x100_lb_gal": "densidad si ×100 (lb/gal)", "densidad_agua_lb_gal": "densidad del agua (lb/gal)"}), ancha=True)
"""),
        M(r"""
**Interpretación.** Como fracción, la densidad queda entre la del petróleo y la del agua (≈ 8.33 lb/gal con un agua de 8.345). Multiplicando por 100 resulta de **≈ 45–47 lb/gal**, es decir, unas cinco veces la densidad del agua: físicamente imposible para una mezcla agua-petróleo. Por tanto el número de la celda **solo tiene sentido como fracción** dentro de esa fórmula. Esto apoya mantener el valor sin convertir, pero **no responde** a la pregunta CT-02 de fondo (por qué el rótulo dice «%»).
"""),
        M(r"""
## Paso 6 · Evaluación E: ¿es evaluable la capacidad predictiva?

Hablar de «capacidad predictiva» exige requisitos mínimos. En vez de afirmar o negar, se **comprueban uno a uno con los datos**.
"""),
        C(r"""
puntos_por_pozo = 1                                           # cada hoja es un punto de operación (cuaderno 01)
fechas_validas = sum(not h["fecha_es_today"] for h in hojas)  # hojas con fecha que no es TODAY()
requisitos = pd.DataFrame([
    {"requisito": "Variable objetivo con medición independiente de las entradas", "cumple": False,
     "evidencia": "el PIP calculado parte de la presión del sensor; no hay un PIP medido aparte"},
    {"requisito": "Más de un punto por pozo para separar ajuste y prueba", "cumple": puntos_por_pozo > 1,
     "evidencia": f"{puntos_por_pozo} punto por hoja"},
    {"requisito": "Eje temporal confiable", "cumple": fechas_validas == len(hojas),
     "evidencia": f"{len(hojas) - fechas_validas} hojas con TODAY(); 1 con fecha sin explicar"},
    {"requisito": "Tolerancia de error aceptable definida", "cumple": False, "evidencia": "no figura en las fuentes (CT-09)"},
    {"requisito": "Parámetros específicos de cada pozo", "cumple": False,
     "evidencia": "°API, presión de yacimiento y de burbuja idénticos en 5 pozos (cuaderno 03)"},
    {"requisito": "Ambigüedades de fórmula resueltas", "cumple": False, "evidencia": "CT-02, CT-03, CT-04, CT-05 abiertas"},
])
evaluable = bool(requisitos["cumple"].all())
print("Capacidad predictiva evaluable:", "SÍ" if evaluable else "NO", "| requisitos cumplidos:", int(requisitos["cumple"].sum()), "de", len(requisitos))
T(requisitos, ancha=True)
"""),
        M(r"""
**Interpretación.** Ningún requisito se cumple. La conclusión no es «el modelo predice mal» sino algo más básico: **con estos datos la pregunta no puede plantearse**. Hablar de predicción exigiría, como mínimo, mediciones repetidas por pozo, un PIP medido de forma independiente y una tolerancia definida por el responsable técnico. Hasta entonces, los resultados de este expediente son **reproducciones y contrastes descriptivos**.
"""),
        M(r"""
## Paso 7 · Criterios de aceptación
"""),
        C(r"""
crit = Criterios("05_evaluacion_por_pozo")
crit.comprobar("C05-1", "Reproducción con error relativo < 1e-9", float(repro.drop(columns="hoja").to_numpy().max()) < 1e-9, f"{repro.drop(columns='hoja').to_numpy().max():.2e}")
crit.comprobar("C05-2", "Contraste calculado-medido en 5 de 5 hojas", len(contraste) == 5 and bool(contraste["% sobre calculado (hoja)"].notna().all()), "n = 5")
alertas_sin_escalar = int((ventana["regla (sin escalar, defectuosa)"] == "RC-BES-01").sum())
crit.comprobar("C05-3", "Misma base: 5 dentro; sin escalar: exactamente una alerta (artefacto)",
               bool((ventana["regla (misma base)"] == "RC-BES-03").all()) and alertas_sin_escalar == 1, f"alertas sin escalar = {alertas_sin_escalar}")
domina = all(impacto[(impacto["hoja"] == n) & (impacto["consulta"] == "CT-03")]["d_q_bfpd"].abs().iloc[0] >
             impacto[(impacto["hoja"] == n) & (impacto["consulta"] != "CT-03")]["d_q_bfpd"].abs().max() for n in contraste["hoja"])
crit.comprobar("C05-4", "CT-03 mueve el caudal más que CT-04 y CT-05 en cada hoja", domina, "5/5 hojas")
crit.comprobar("C05-5", "Capacidad predictiva declarada no evaluable con requisitos listados", (not evaluable) and len(requisitos) == 6, f"{int(requisitos['cumple'].sum())}/6 cumplidos")
crit.comprobar("C05-6", "Seis figuras existen", len(rutas) == 6 and all(r.is_file() for r in rutas), ", ".join(r.name for r in rutas))
crit.comprobar("C05-7", "El libro no cambió", huellas(COPIA_TRABAJO)["sha256"] == sha_inicial, sha_inicial[:16] + "…")
T(crit.tabla())
"""),
        C(r"""
crit.exigir()
print("Todos los criterios de aceptación del cuaderno 05 se cumplen.")
"""),
        M(r"""
## Conclusión técnica

- **Reproducción:** exacta (≤ 1e-15). **Contraste:** el caudal calculado difiere del medido entre −5.9 % y +8.8 % sin sesgo direccional; con n = 5 es descriptivo. **Ventana operativa:** las cinco hojas están dentro de sus límites a la frecuencia de operación; la alerta de QF-084 de la primera versión era un artefacto de comparar bases de frecuencia distintas y se corrigió.
- **Ambigüedad dominante:** el signo de PIP (CT-03), que mueve el caudal calculado entre 106 y 456 BFPD según la hoja. Las otras (exponente, temperatura) pesan mucho menos. Esto fija el orden de resolución.
- **Lo que no se puede afirmar:** validación del modelo, capacidad predictiva, ni que un pozo esté «bien» o «mal». Los seis requisitos de predicción faltan, por la naturaleza de los datos y no por el código.
- **Lección metodológica:** una regla candidata es tan fiable como la base sobre la que compara. El control `C05-3` deja la comparación defectuosa como prueba permanente para que no vuelva a pasar inadvertida.
- **Siguiente paso:** cuaderno 06, hallazgos y reglas candidatas.
"""),
    ]


if __name__ == "__main__":
    print(guardar(NOMBRE, construir()))
