"""Cuaderno 02 (glosario de ecuaciones y variables)."""

from informes.cuadernos.base import C, M, PREPARACION, guardar

NOMBRE = "02_ecuaciones_y_variables"


def construir():
    return [
        M(r"""
# Cuaderno 02 · Ecuaciones y variables del cálculo

**Expediente:** BES-jun · **Estado del expediente:** Listo para revisión (no Completo)

> **Relación con `02_trazabilidad_y_analisis_formulas`.** Este cuaderno **explica** cada ecuación (fenómeno, formulación, variables, unidades, hipótesis, función de código). El de trazabilidad **audita** las fórmulas del libro (firmas idénticas, constantes, hidrostática, catálogo).

## 1. Introducción y contexto (el problema)
El libro calcula tres magnitudes, la altura que ve la bomba en su entrada (**PIP**), la altura que debe vencer en su descarga (**THD**) y el caudal al que la bomba la entrega (**Q a producir**), encadenando diez ecuaciones. Quien consuma esos números necesita saber **qué dice cada ecuación, de dónde viene y hasta dónde vale**. Una ecuación copiada sin su contexto es la fuente más habitual de errores de unidades y de uso fuera de dominio.

## 2. Justificación y necesidad
Un glosario técnico en el que cada ecuación aparezca con su fenómeno físico, su formulación, sus variables y unidades, sus hipótesis, su correspondencia con una función de Python y una **categoría honesta** de su origen: no es lo mismo una ecuación de definición (como el °API), una relación empírica con constantes sin fuente, que una hipótesis de aplicación (como llevar la curva de bomba a otra frecuencia).

## 3. Objetivo general
Documentar y verificar las diez ecuaciones y las variables de la cadena de cálculo de BES-jun, distinguiendo con evidencia lo documentado, lo empírico y lo supuesto, sin inventar orígenes.

## 4. Dominio y alcance
**Incluye:** ecuaciones transcritas del libro (fluido, balance de alturas, bomba), glosario de variables con rango observado, análisis dimensional y comprobaciones de límite ejecutables.

**No incluye:** validar físicamente las ecuaciones, resolver las consultas CT-02 a CT-08, ni cálculos de potencia, motor o cable (fuera del alcance actual).

## 5. Fuentes y datos (entradas y salidas)
**Entradas:** `entrada/BES_jun.xlsx`, módulos `modelo_deterministico.*` y `analisis.catalogo_bes_jun`. **Salidas:** tablas del cuaderno; ningún archivo escrito.

## 6. Objetivos específicos y criterios de aceptación
**C02b-1** las diez ecuaciones tienen una función de código existente y llamable · **C02b-2** cada ecuación tiene un tipo y una reserva declarados · **C02b-3** el glosario calcula el rango de las 14 entradas con datos de las 5 hojas · **C02b-4** las 10 comprobaciones de límite se cumplen · **C02b-5** toda consulta citada existe en el registro CT · **C02b-6** el libro no cambió.

## 7. Riesgo si este paso falla
Aplicar una ecuación sin su dominio (p. ej. una pérdida por fricción con un caudal o diámetro fuera de lo que cubre), confundir unidades (psi/ft por psi·ft) o presentar una constante empírica como una ley.
"""),
        M(r"""
## Preparación del entorno
"""),
        C(PREPARACION),
        C(r"""
import importlib, inspect, re
import numpy as np
from ingesta.integridad import huellas
from ingesta.leer_bes_jun import COPIA_TRABAJO, leer_libro
from analisis.cadena import calcular_hoja
sha_inicial = huellas(COPIA_TRABAJO)["sha256"]
hojas = leer_libro()
calc = {h["hoja"]: calcular_hoja(h) for h in hojas}
print(len(hojas), "hojas;", "cadena calculable en", sum(all(r.estado == "calculable" for r in c.values()) for c in calc.values()), "de", len(calc))
"""),
        M(r"""
## Paso 1 · Cómo se clasifica cada ecuación

Para no inventar orígenes, cada ecuación se etiqueta con **una** de estas categorías, según la evidencia disponible en las fuentes del expediente:

| Categoría | Qué significa | Qué se puede decir |
|---|---|---|
| **Teórica documentada** | Es una definición o ley estándar, y aparece en una fuente del expediente (libro, XLSM o PDF) | Su forma es conocida; falta verificar que el libro la aplique a este caso |
| **Empírica de la hoja** | El libro la escribe con constantes que no tienen definición en ninguna fuente leída | Se transcribe tal cual; no se presenta como correlación publicada |
| **Hipótesis de aplicación** | Es una ley teórica que se **supone** válida para este equipo y condiciones | Su validez en este caso es una pregunta abierta (CT) |
| **Procedimiento numérico** | Es un método de cálculo (interpolación, búsqueda) | Se reproduce; su error depende de la discretización de los datos |

Además, toda ecuación listada está **implementada** en una función concreta de Python; la verificación del Paso 5 comprueba que esa función existe.
"""),
        M(r"""
## Paso 2 · Bloque A: propiedades del fluido (E-01 a E-04)

### E-01 · Gravedad específica del crudo a 60 °F

**Fenómeno.** La densidad relativa del crudo respecto del agua. El grado API es una escala de la industria: a mayor °API, crudo más liviano.

$$\gamma_{60}=\frac{141.5}{131.5+\mathrm{API}}$$

**Variables.** \(\gamma_{60}\): gravedad específica a 60 °F (adimensional); API: grado API (°API). **Hipótesis.** Definición estándar; con API = 10 el crudo tiene la densidad del agua (γ = 1). **Código.** `modelo_deterministico.fluidos_bes_jun.gravedad_especifica_api`. **Categoría.** Teórica documentada (definición del °API; el XLSM la trae en `J4` y las hojas en la celda «Gravedad Oil @ 60ºF»). **Limitación.** Dominio: API > −131.5 para no dividir por cero; el código rechaza valores no finitos.

### E-02 · Corrección de la gravedad por temperatura

**Fenómeno.** El crudo se dilata al calentarse y su densidad relativa baja; en el fondo la temperatura es mayor que la de referencia.

$$\gamma_T=\gamma_{60}-0.00066\,(T-15.556)+3\times10^{-7}\,(T-15.556)^2$$

**Variables.** \(T\): temperatura (°C); 15.556 °C = 60 °F (la temperatura de referencia). **Hipótesis.** Los coeficientes 0.00066 y \(3\times10^{-7}\) corresponden a una dilatación por °C; **no tienen definición** en las fuentes leídas. **Código.** `gravedad_oil_a_temperatura`. **Categoría.** Empírica de la hoja. **Limitación.** Origen desconocido de las constantes (CT-04); su efecto sobre el caudal es de segundo orden (cuaderno 05).

### E-03 · Densidad de la mezcla agua-petróleo

**Fenómeno.** La densidad de un fluido que es una mezcla de agua y crudo en proporciones dadas.

$$\rho=8.33\left[\frac{\mathrm{BSW}\,\rho_w}{8.33}+(1-\mathrm{BSW})\,\gamma_T\right]$$

**Variables.** \(\rho\): densidad de la mezcla (lb/gal); BSW: fracción de agua y sedimentos (adimensional, 0 a 1); \(\rho_w\): densidad del agua (lb/gal); 8.33 lb/gal ≈ densidad del agua dulce. **Hipótesis.** Mezcla ideal (los volúmenes se suman) y BSW **como fracción**. **Código.** `densidad_lb_por_galon`. **Categoría.** Teórica documentada (mezcla ideal) escrita en la hoja. **Limitación.** El rótulo de BS&W dice «%» pero la fórmula lo usa como fracción (CT-02); el código toma el número tal cual.

### E-04 · Gradiente de presión

**Fenómeno.** Cuánto aumenta la presión por cada pie de profundidad de una columna de ese fluido.

$$G=0.052\,\rho$$

**Variables.** \(G\): gradiente (psi/ft); \(\rho\): densidad (lb/gal); 0.052: factor de conversión de uso estándar en campo (psi/ft por lb/gal). **Hipótesis.** Fluido incompresible de densidad uniforme. **Código.** `gradiente_psi_por_ft`. **Categoría.** Teórica de uso estándar escrita en la hoja. **Limitación.** La hoja rotula la salida «psi\*ft» (es psi/ft); el XLSM usa 0.433·γ (agua = 0.433 psi/ft), que difiere de 0.052·ρ en menos de 0.3 % para el agua (se calcula en el Paso 5).
"""),
        M(r"""
## Paso 3 · Bloque B: balance de alturas (E-05 a E-08)

La bomba debe levantar el fluido desde su **entrada** hasta la **superficie**, venciendo la fricción y la presión en el cabezal. Todas las presiones se expresan como **altura equivalente de fluido** (pies), dividiendo entre el gradiente \(G\).

### E-05 · PIP (altura de presión en la entrada de la bomba)

**Fenómeno.** La presión que el fluido ejerce a la entrada de la bomba, medida por un sensor ubicado a otra profundidad, trasladada a la entrada.

$$\mathrm{PIP}_{ft}=\frac{P_{s}-(\mathrm{TVD}_{i}-\mathrm{TVD}_{s})\,G}{G}$$

**Variables.** \(P_s\): presión del sensor (psi); \(\mathrm{TVD}_i\), \(\mathrm{TVD}_s\): profundidad vertical del intake y del sensor (ft); \(G\): gradiente (psi/ft). Resultado en pies de fluido. **Hipótesis.** Gradiente constante entre sensor e intake; la corrección usa TVD (no MD). **Código.** `modelo_deterministico.balance_bes_jun.pip_en_ft`. **Categoría.** Empírica de la hoja (hay una analogía documentada en E1, F-12, con el signo opuesto). **Limitación crítica.** Con el sensor **más profundo** que el intake (las cinco hojas), la presión en el intake debería ser **menor** que la del sensor; la fórmula de la hoja entrega una **mayor**, porque el término \((\mathrm{TVD}_i-\mathrm{TVD}_s)\) es negativo y se resta. Es la ambigüedad CT-03 de prioridad alta: el código conserva el signo de la hoja.

### E-06 · THP en pies

$$\mathrm{THP}_{ft}=\frac{\mathrm{THP}}{G}$$

**Fenómeno.** La contrapresión de la línea en el cabezal (*tubing head pressure*) expresada como columna de fluido. **Variables.** THP (psi); \(G\) (psi/ft). **Hipótesis.** Misma densidad que en el fondo. **Código.** `thp_en_ft`. **Categoría.** Teórica (conversión de presión a altura). **Limitación.** Ninguna consulta abierta.

### E-07 · Pérdida de presión por fricción (Hazen-Williams)

**Fenómeno.** El fluido pierde energía al rozar con la pared del tubing; la pérdida crece fuertemente con el caudal y decrece con el diámetro.

$$h_f=\left[2.083\left(\frac{100}{C}\right)^{1.85}\left(\frac{Q}{34.3}\right)^{1.85}\frac{1}{\mathrm{ID}^{4.8566}}\right]\frac{L}{1000}$$

**Variables.** \(h_f\): pérdida (ft); \(C=120\): coeficiente de Hazen-Williams (dentro de la fórmula); \(Q\): caudal (BFPD); ID: diámetro interior (in); \(L\): longitud (ft), que la hoja toma como la **TVD de descarga**; 34.3 BFPD ≈ 1 gpm. **Hipótesis.** Flujo turbulento de agua en tubería; aplicada aquí a un fluido de 12 °API con alto corte de agua. **Código.** `friccion_hazen_williams_ft`. **Categoría.** Empírica de uso general, con constantes de la hoja. **Limitaciones.** El exponente del diámetro es 4.8566 en la hoja y 4.8655 en el PDF 004 (CT-05); la ecuación se planteó para agua a 20 °C; y usa la TVD en lugar de la longitud medida.

### E-08 · THD total

$$\mathrm{THD}=\mathrm{TVD}_{d}+h_f+\mathrm{THP}_{ft}-\mathrm{PIP}_{ft}$$

**Fenómeno.** Altura total que la bomba debe aportar: elevar el fluido hasta la profundidad de descarga, vencer la fricción y la contrapresión, descontando la presión que ya trae el fluido a la entrada. **Variables.** Todas en pies. **Hipótesis.** Suma de términos independientes. **Código.** `thd_total_ft`. **Categoría.** Procedimiento de balance escrito en la hoja. **Limitación.** Se llama «THD TOTAL» en la hoja; no se afirma que sea el TDH del PDF 004 (cuya definición es distinta).
"""),
        M(r"""
## Paso 4 · Bloque C: la bomba (E-09 y E-10)

### E-09 · Leyes de afinidad (curva de bomba a otra velocidad)

**Fenómeno.** Si una bomba centrífuga cambia de velocidad, su caudal cambia en proporción a la velocidad y su altura con el cuadrado de la velocidad.

$$Q'=Q_{60}\,\frac{f}{f_c},\qquad H'=H_{60}\left(\frac{f}{f_c}\right)^{2}N$$

**Variables.** \(Q_{60}\), \(H_{60}\): caudal (BFPD) y altura **por etapa** (ft) de la tabla a la frecuencia de la curva \(f_c=60\) Hz; \(f\): frecuencia de operación (Hz); \(N\): número de etapas. **Hipótesis.** Las leyes de afinidad son válidas para esta bomba y rango de frecuencias (56–67 Hz respecto de 60 Hz). **Código.** `modelo_deterministico.interseccion_bes_jun.curva_a_velocidad`. **Categoría.** Hipótesis de aplicación (la ley es teórica; su validez para estas bombas es la consulta CT-08). **Limitación.** Los límites de caudal se escalan con \(f/60\); la validez de ese escalado no está verificada.

### E-10 · Caudal a producir (intersección sistema-bomba)

$$\mathrm{THD}=H'(Q^{*})\ \Rightarrow\ Q^{*}\ \text{por interpolación lineal entre los dos puntos que encierran la THD}$$

**Fenómeno.** El punto donde la altura que entrega la bomba iguala a la que exige el sistema. **Variables.** \(Q^{*}\): caudal a producir (BFPD). **Hipótesis.** La curva de bomba es una poligonal de seis puntos y es lineal entre ellos. **Código.** `caudal_a_producir` (réplica de `MATCH(-1)` e `INDEX`). **Categoría.** Procedimiento numérico. **Limitaciones.** La THD se calcula con el caudal **medido** (en la fricción), no con \(Q^{*}\): el sistema no se resuelve de forma autoconsistente (se estudia en `04_modelo_deterministico`); y fuera del tramo de la curva el código devuelve una alerta en vez de extrapolar.
"""),
        M(r"""
## Paso 5 · Verificación de que cada ecuación existe en el código

**Qué se hace.** Para cada ecuación se importa el módulo, se obtiene la función por su nombre y se lee su firma. Así, la documentación **no puede describir una función que no existe**. Se añade la categoría, la reserva (consulta abierta) y el análisis dimensional de la ecuación.
"""),
        C(r"""
ECUACIONES = [
    # id, nombre, módulo, función, tipo, reserva, análisis dimensional
    ("E-01", "Gravedad específica 60 °F", "modelo_deterministico.fluidos_bes_jun", "gravedad_especifica_api", "teórica documentada", "—", "adimensional / adimensional"),
    ("E-02", "Corrección por temperatura", "modelo_deterministico.fluidos_bes_jun", "gravedad_oil_a_temperatura", "empírica de la hoja", "CT-04", "adimensional; cada coeficiente es por °C^n (ajuste)"),
    ("E-03", "Densidad de la mezcla", "modelo_deterministico.fluidos_bes_jun", "densidad_lb_por_galon", "teórica documentada", "CT-02", "lb/gal · (adim.) = lb/gal ✓"),
    ("E-04", "Gradiente de presión", "modelo_deterministico.fluidos_bes_jun", "gradiente_psi_por_ft", "teórica de uso estándar", "CT-02", "(lb/gal)·(psi/ft)/(lb/gal) = psi/ft ✓"),
    ("E-05", "PIP en pies", "modelo_deterministico.balance_bes_jun", "pip_en_ft", "empírica de la hoja", "CT-03", "(psi − ft·psi/ft)/(psi/ft) = ft ✓"),
    ("E-06", "THP en pies", "modelo_deterministico.balance_bes_jun", "thp_en_ft", "teórica documentada", "—", "psi/(psi/ft) = ft ✓"),
    ("E-07", "Fricción Hazen-Williams", "modelo_deterministico.balance_bes_jun", "friccion_hazen_williams_ft", "empírica de uso general", "CT-05", "no homogénea: constantes de ajuste en unidades mixtas (BFPD, in, ft)"),
    ("E-08", "THD total", "modelo_deterministico.balance_bes_jun", "thd_total_ft", "balance de la hoja", "CT-03, CT-05", "ft + ft + ft − ft = ft ✓"),
    ("E-09", "Leyes de afinidad", "modelo_deterministico.interseccion_bes_jun", "curva_a_velocidad", "hipótesis de aplicación", "CT-08", "BFPD·(Hz/Hz) y ft·(Hz/Hz)²·adim. ✓"),
    ("E-10", "Caudal a producir", "modelo_deterministico.interseccion_bes_jun", "caudal_a_producir", "procedimiento numérico", "CT-03, CT-08, CT-09", "BFPD (interpolación entre BFPD) ✓"),
]
filas = []
for i, nombre, mod, fn, tipo, reserva, dim in ECUACIONES:
    f = getattr(importlib.import_module(mod), fn, None)
    filas.append({"id": i, "ecuación": nombre, "función": f"{mod.split('.')[-1]}.{fn}", "existe y es llamable": callable(f),
                  "parámetros": ", ".join(inspect.signature(f).parameters) if callable(f) else "—", "tipo": tipo, "reserva": reserva, "análisis dimensional": dim})
tabla_eq = pd.DataFrame(filas)
T(tabla_eq, ancha=True)
"""),
        M(r"""
**Interpretación.** Las diez ecuaciones tienen su función y su firma; el análisis dimensional confirma que las ecuaciones de conversión y de balance son **homogéneas** en unidades (psi/ft, ft). La única **no homogénea** es la de fricción, porque es una correlación empírica con constantes de ajuste (2.083, 34.3, 4.8566) que ya absorben las conversiones: ahí no se pueden comprobar las unidades por análisis dimensional, y por eso se prueba por su comportamiento (Paso 7). Ocho de las diez tienen una consulta abierta: no son ecuaciones «malas», son transcripciones cuyo origen o aplicabilidad aún no está cerrado.
"""),
        M(r"""
## Paso 6 · Glosario de variables con su rango observado

**Qué se hace.** Para cada entrada de la cadena se muestra el símbolo, el nombre, la unidad y el **rango observado en las cinco hojas** (calculado desde los datos). El rango es el dominio en el que el cálculo ha sido usado: fuera de él se estaría **extrapolando**.
"""),
        C(r"""
VARIABLES = [
    ("API", "api_deg", "Grado API del crudo", "°API", "entrada"),
    ("T", "temperatura_c", "Temperatura de fondo", "°C", "entrada"),
    ("BSW", "bsw_numero", "BS&W (número de la celda, usado como fracción)", "adim. (rótulo «%»)", "entrada"),
    ("ρ_w", "densidad_agua_lb_gal", "Densidad del agua", "lb/gal", "entrada"),
    ("P_s", "presion_sensor_psi", "Presión del sensor", "psi", "entrada"),
    ("THP", "thp_psi", "Presión en cabezal de tubing", "psi", "entrada"),
    ("Q", "caudal_operacion_bfpd", "Caudal de operación", "BFPD", "entrada"),
    ("ID", "id_tubing_in", "Diámetro interior del tubing", "in", "entrada"),
    ("TVD_d", "tvd_descarga_ft", "TVD de la descarga", "ft", "entrada (del survey)"),
    ("TVD_i", "tvd_intake_ft", "TVD del intake", "ft", "entrada (del survey)"),
    ("TVD_s", "tvd_sensor_ft", "TVD del sensor", "ft", "entrada (del survey)"),
    ("f", "frecuencia_hz", "Frecuencia de operación", "Hz", "entrada"),
    ("f_c", "frecuencia_curva_hz", "Frecuencia de la curva de bomba", "Hz", "entrada"),
    ("N", "etapas", "Número de etapas", "adim.", "entrada"),
]
SALIDAS = [("γ60", "fl", "sg_60", "adim."), ("γT", "fl", "sg_temperatura", "adim."), ("ρ", "fl", "densidad_lb_gal", "lb/gal"), ("G", "fl", "gradiente_psi_ft", "psi/ft"),
           ("PIP", "ba", "pip_ft", "ft"), ("THP_ft", "ba", "thp_ft", "ft"), ("h_f", "ba", "friccion_ft", "ft"), ("THD", "ba", "thd_total_ft", "ft"), ("Q*", "q", "caudal_a_producir_bfpd", "BFPD")]
filas = []
for sim, k, nombre, unidad, rol in VARIABLES:
    v = [h[k] for h in hojas]
    filas.append({"símbolo": sim, "variable": nombre, "unidad": unidad, "rol": rol, "mínimo": min(v), "máximo": max(v), "valores distintos": len(set(v))})
for sim, bloque, k, unidad in SALIDAS:
    v = [calc[h["hoja"]][bloque].resultados[k]["valor"] for h in hojas]
    filas.append({"símbolo": sim, "variable": k, "unidad": unidad, "rol": "calculada", "mínimo": min(v), "máximo": max(v), "valores distintos": len(set(v))})
glosario = pd.DataFrame(filas)
T(glosario, ancha=True)
"""),
        M(r"""
**Interpretación.** Cuatro entradas **no varían** entre pozos: °API (12), densidad del agua (8.345 lb/gal), diámetro interior del tubing (2.996 in) y frecuencia de la curva (60 Hz); la temperatura toma solo dos valores y el BS&W cuatro. Esto es relevante porque, **para esas variables, estas cinco hojas no permiten saber qué ocurre si cambian**: no hay variación observada. Las variables que sí varían son la presión del sensor (607–821 psi), el THP (145–210 psi), el caudal (5 419–10 301 BFPD), las TVD de los equipos, la frecuencia (56–67 Hz) y las etapas (31–53). Entre las calculadas, el gradiente es casi constante (0.4330 a 0.4335 psi/ft) porque con un BS&W de 0.96–0.98 el fluido es prácticamente agua; el PIP va de 1 422 a 1 921 ft, la THD de 1 517 a 2 083 ft y el caudal a producir de 5 503 a 10 535 BFPD. **La fricción es la que más varía en términos relativos**: de 220 a 731 ft (≈3.3 veces) mientras que el caudal solo varía ≈1.9 veces, porque la fricción crece con el caudal elevado a 1.85 (\(1.9^{1.85}\approx 3.3\)).
"""),
        M(r"""
## Paso 7 · Comprobaciones de límite: ¿se comporta cada ecuación como debe?

**Qué se hace.** Una ecuación bien transcrita debe cumplir propiedades que se conocen **sin necesidad de datos**: casos en los que el resultado es obvio. Se prueban diez. Si una transcripción tuviera un exponente o un signo mal escrito, alguna de estas propiedades fallaría. **Qué no prueban:** que la fórmula sea la adecuada para el fluido y el pozo (eso es validación y no hay datos para hacerla).
"""),
        C(r"""
from modelo_deterministico.fluidos_bes_jun import gravedad_especifica_api, densidad_lb_por_galon, gradiente_psi_por_ft
from modelo_deterministico.balance_bes_jun import pip_en_ft, friccion_hazen_williams_ft, thd_total_ft, EXPONENTE_ID_HAZEN_BES_JUN
from modelo_deterministico.interseccion_bes_jun import curva_a_velocidad
h0 = hojas[0]; r0 = calc[h0["hoja"]]
g0 = r0["fl"].resultados["gradiente_psi_ft"]["valor"]
f0 = friccion_hazen_williams_ft(h0["caudal_operacion_bfpd"], h0["id_tubing_in"], h0["tvd_descarga_ft"])
curva = h0["curva"]; razon = 2.0
dobla = curva_a_velocidad(curva, 2 * h0["frecuencia_curva_hz"], h0["frecuencia_curva_hz"], 1)
misma = curva_a_velocidad(curva, h0["frecuencia_curva_hz"], h0["frecuencia_curva_hz"], h0["etapas"])
thd_suma = max(abs(calc[h["hoja"]]["ba"].resultados["thd_total_ft"]["valor"] - (h["tvd_descarga_ft"] + calc[h["hoja"]]["ba"].resultados["friccion_ft"]["valor"]
               + calc[h["hoja"]]["ba"].resultados["thp_ft"]["valor"] - calc[h["hoja"]]["ba"].resultados["pip_ft"]["valor"])) for h in hojas)
rel = lambda a, b: abs(a - b) / abs(b)
pruebas = [
    ("L-01", "E-01", "API = 10 da γ = 1 (misma densidad que el agua)", gravedad_especifica_api(10.0), 1.0),
    ("L-02", "E-03", "BSW = 0 da ρ = 8.33·γT (todo crudo)", densidad_lb_por_galon(0.0, 8.345, 0.95), 8.33 * 0.95),
    ("L-03", "E-03", "BSW = 1 da ρ = ρ_w (todo agua)", densidad_lb_por_galon(1.0, 8.345, 0.95), 8.345),
    ("L-04", "E-04", "Gradiente del agua (0.052·8.345) frente a 0.433 del XLSM: diferencia relativa < 0.5 %", rel(gradiente_psi_por_ft(8.345), 0.433) < 0.005, True),
    ("L-05", "E-05", "Con TVD_i = TVD_s el PIP en pies es P_s/G", pip_en_ft(h0["presion_sensor_psi"], 2500.0, 2500.0, g0), h0["presion_sensor_psi"] / g0),
    ("L-06", "E-07", "Duplicar Q multiplica h_f por 2^1.85", friccion_hazen_williams_ft(2 * h0["caudal_operacion_bfpd"], h0["id_tubing_in"], h0["tvd_descarga_ft"]) / f0, 2 ** 1.85),
    ("L-07", "E-07", "Duplicar ID multiplica h_f por 2^−4.8566", friccion_hazen_williams_ft(h0["caudal_operacion_bfpd"], 2 * h0["id_tubing_in"], h0["tvd_descarga_ft"]) / f0, 2 ** -EXPONENTE_ID_HAZEN_BES_JUN),
    ("L-08", "E-08", "THD = TVD_d + h_f + THP_ft − PIP_ft en las 5 hojas (diferencia máx. < 1e-9 ft)", thd_suma < 1e-9, True),
    ("L-09", "E-09", "Con f = f_c la curva no cambia de caudal y su head se multiplica solo por N", all(a["caudal_bfpd"] == b["caudal_bfpd"] and abs(a["head_ft"] - b["head_ft"] * h0["etapas"]) < 1e-9 for a, b in zip(misma, curva)), True),
    ("L-10", "E-09", "Con f = 2·f_c: caudal ×2 y head ×4", all(abs(a["caudal_bfpd"] - 2 * b["caudal_bfpd"]) < 1e-9 and abs(a["head_ft"] - 4 * b["head_ft"]) < 1e-9 for a, b in zip(dobla, curva)), True),
]
filas = []
for pid, eq, texto, obtenido, esperado in pruebas:
    ok = (obtenido == esperado) if isinstance(esperado, bool) else rel(obtenido, esperado) < 1e-12
    filas.append({"prueba": pid, "ecuación": eq, "propiedad": texto, "obtenido": obtenido, "esperado": esperado, "cumple": ok})
limites = pd.DataFrame(filas)
T(limites, ancha=True)
"""),
        M(r"""
**Interpretación.** Las diez propiedades se cumplen. Los casos extremos de la mezcla (todo crudo, todo agua) devuelven exactamente la densidad esperada; la comprobación de la fricción confirma el comportamiento de ley de potencias (duplicar el caudal multiplica la pérdida por 3.605 = 2^1.85, y duplicar el diámetro la divide por ≈29, es decir, la multiplica por 0.0345 = 2^−4.8566); la THD es exactamente la suma de sus cuatro términos en las cinco hojas y las leyes de afinidad hacen lo que dicen (caudal ×2 y altura ×4 al duplicar la frecuencia). El gradiente del agua con 0.052 difiere de 0.433 del XLSM en ≈0.2 %. **Lectura práctica de la fricción:** por el exponente 4.8566, un error de 1 % en el diámetro interior del tubing cambia la fricción en ≈4.9 %, y un error de 1 % en el caudal, en ≈1.85 %. Es la ecuación más sensible a la calidad de los datos de entrada; cuánto pesa eso en el caudal a producir se cuantifica en `04_modelo_deterministico`.
"""),
        M(r"""
## Paso 8 · Criterios de aceptación
"""),
        C(r"""
crit = Criterios("02_ecuaciones_y_variables")
crit.comprobar("C02b-1", "Las 10 ecuaciones tienen función existente y llamable", bool(tabla_eq["existe y es llamable"].all()) and len(tabla_eq) == 10, f"{int(tabla_eq['existe y es llamable'].sum())} de 10")
doc_ct = (RAIZ / "docs" / "consultas_tecnicas_pendientes.md").read_text(encoding="utf-8")
ct_doc = set(re.findall(r"^\| (CT-\d+) \|", doc_ct, flags=re.M))
ct_usadas = set(re.findall(r"CT-\d+", " ".join(tabla_eq["reserva"])))
crit.comprobar("C02b-2", "Cada ecuación tiene tipo y reserva declarados", bool((tabla_eq["tipo"].str.len() > 0).all() and (tabla_eq["reserva"].str.len() > 0).all()), "10 de 10")
crit.comprobar("C02b-3", "Glosario con rango de las 14 entradas y 9 salidas", len(glosario) == 23 and bool(glosario["mínimo"].notna().all()), f"{len(glosario)} variables")
crit.comprobar("C02b-4", "Las 10 comprobaciones de límite se cumplen", bool(limites["cumple"].all()), f"{int(limites['cumple'].sum())} de {len(limites)}")
crit.comprobar("C02b-5", "Toda consulta citada existe en el registro CT", ct_usadas <= ct_doc, f"citadas: {sorted(ct_usadas)}")
crit.comprobar("C02b-6", "El libro no cambió", huellas(COPIA_TRABAJO)["sha256"] == sha_inicial, sha_inicial[:16] + "…")
T(crit.tabla())
"""),
        C(r"""
crit.exigir()
print("Todos los criterios de aceptación del cuaderno 02 (ecuaciones) se cumplen.")
"""),
        M(r"""
## Conclusión técnica

- **Resultado:** las diez ecuaciones de la cadena están documentadas con fenómeno, formulación, variables, unidades, hipótesis, función de código, tipo y reserva; cada una tiene una función existente y diez propiedades de límite se cumplen.
- **Clasificación honesta:** tres son teóricas documentadas (E-01, E-03, E-06), una es teórica de uso estándar (E-04), tres son empíricas de la hoja o de uso general con constantes propias (E-02, E-05, E-07), una es un balance de la hoja (E-08), una es una hipótesis de aplicación (E-09) y una es un procedimiento numérico (E-10).
- **Dónde está el riesgo:** el signo de E-05 (CT-03) y el exponente de E-07 (CT-05) son las transcripciones con más peso; E-09 descansa en una hipótesis (CT-08) que ninguna fuente del expediente verifica.
- **Lo que el glosario advierte:** cuatro entradas no varían entre pozos; el cálculo no puede ofrecer evidencia sobre su efecto.
- **Qué no se afirma:** que las ecuaciones describan bien estos pozos. Solo que están **bien transcritas** y que **se comportan como las ecuaciones que dicen ser**.
- **Siguiente paso:** `02_trazabilidad_y_analisis_formulas`, que audita las fórmulas del libro de las que salen estas ecuaciones.
"""),
    ]


if __name__ == "__main__":
    print(guardar(NOMBRE, construir()))
