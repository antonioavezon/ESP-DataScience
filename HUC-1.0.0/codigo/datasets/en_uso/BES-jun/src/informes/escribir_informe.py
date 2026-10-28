"""Escribe el informe de BES-jun a partir de la copia de trabajo. No guarda el Excel."""

from __future__ import annotations

from analisis.cadena import calcular_hoja
from analisis.catalogo_bes_jun import FORMULAS
from analisis.estadisticas import guardar_tablas, tabla_survey
from analisis.graficos import figura_elasticidades, guardar_figuras
from analisis.sensibilidad_local import ENTRADAS_RELATIVAS, TVD_EQUIPOS, derivada_por_pie, elasticidad_relativa
from evaluacion.motor import MODELOS
from ingesta.leer_bes_jun import leer_libro, raiz_expediente
from reglas.catalogo import REGLAS
from ingesta.survey import leer_survey
from analisis.sensibilidad import gradiente_base
from modelo_deterministico.balance_bes_jun import evaluar_balance, pip_en_ft
from modelo_deterministico.hipotesis_ct03 import pip_ft_si_el_sensor_esta_mas_profundo
from modelo_deterministico.fluidos_bes_jun import evaluar_fluido
from reglas.candidatas_bes_jun import comparar_caudal_con_limites, limites_a_frecuencia


def construir() -> tuple[str, str]:
    hojas = leer_libro()
    estaciones = leer_survey()
    guardar_tablas(hojas, estaciones)
    guardar_figuras(hojas, estaciones)
    return _markdown(hojas, estaciones), _html_despues(hojas)


def _markdown(hojas: list[dict], estaciones: list[dict]) -> str:
    filas = []
    for hoja in hojas:
        fluido = evaluar_fluido(
            hoja["api_deg"],
            hoja["temperatura_c"],
            hoja["bsw_numero"],
            hoja["densidad_agua_lb_gal"],
        )
        grad = None if fluido.estado != "calculable" else fluido.resultados["gradiente_psi_ft"]["valor"]
        balance = evaluar_balance(
            hoja["presion_sensor_psi"],
            hoja["thp_psi"],
            hoja["tvd_intake_ft"],
            hoja["tvd_sensor_ft"],
            hoja["tvd_descarga_ft"],
            grad,
            hoja["caudal_operacion_bfpd"],
            hoja["id_tubing_in"],
        )
        regla = comparar_caudal_con_limites(hoja)[0]
        filas.append((hoja, fluido, balance, regla))
    lineas = [
        "# Informe de análisis · BES-jun",
        "",
        "Estado del expediente: **Listo para revisión**.",
        "",
        "## Objetivo y alcance",
        "",
        "Este informe describe el único Excel en `datasets/en_uso/`: `Copia de FINAL BES-jun.xlsx`.",
        "La copia de trabajo es `entrada/BES_jun.xlsx`.",
        "El cuaderno de inventario imprime la ruta, el tamaño en bytes y el SHA-256 de la copia de trabajo, de `fuentes/originales/` y del archivo recibido en la raíz del proyecto.",
        "Los tres valen `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85` y 329308 bytes.",
        "Esa coincidencia es identidad de bytes. No califica las mediciones ni las fórmulas.",
        "No se abrieron RB-1521 ni RB-IA-2191. No se construyó un motor para otros archivos. No se instaló un GLM.",
        "",
        "## Fuentes y fórmulas",
        "",
        "El catálogo común está en `../../../docs/trazabilidad_ecuaciones.md`.",
        "En este libro se usaron solo las expresiones que la propia hoja escribe y que el código contrasta con la caché.",
        "",
        "| ID | Estado | Aplicación en este Excel |",
        "|---|---|---|",
    ]
    for formula in FORMULAS:
        lineas.append(f"| {formula['id']} | {formula['estado']} | {formula['aplica']} |")
    lineas += [
        "",
        "La corrección de temperatura y el signo del PIP frente a F-12 quedan en aclaración.",
        "Eso no detiene el cálculo directo de la celda: la fuente de la aritmética es la propia celda.",
        "El Método B, el observador y la cadena del XLSM quedan fuera de este análisis.",
        "",
        "## Estructura y calidad",
        "",
        "Cinco hojas, todas visibles. Ninguna oculta. Cada hoja tiene un punto de operación, una tabla de seis puntos a 60 Hz y un survey `Measured`.",
        "El libro no declara si la llave es el nombre de la hoja, el rótulo Cluster o el rótulo Pozo.",
        "Cada hoja se analizó sola.",
        "Cuatro fechas son `=TODAY()`; el valor cacheado 2026-10-17 es la fecha de cálculo del libro.",
        "QF-549HST tiene escrita 2017-09-06. No hay serie de días ni periodos que interpolar.",
        "En QF-549HST hay 13 cachés `#DIV/0!` en promedios del bloque eléctrico. No entran en PIP ni en THD.",
        "No se imputó ningún valor. El registro está en `data_procesados/transformaciones.md`.",
        "",
        "## Pozos",
        "",
        "La columna Pozo es el texto de esa celda. La columna Hoja es el nombre de la hoja.",
        "",
        '<div class="tabla-ancha">',
        "",
        "| Hoja | Pozo | Bomba | Hz | Caudal BFPD | PIP ft | THD ft | Regla candidata |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for hoja, _fluido, balance, regla in filas:
        pip = balance.resultados["pip_ft"]["valor"]
        thd = balance.resultados["thd_total_ft"]["valor"]
        lineas.append(
            f"| {hoja['hoja']} | {hoja['pozo']} | {hoja['bomba_referencia']} | {hoja['frecuencia_hz']:.0f} | {hoja['caudal_operacion_bfpd']:.0f} | {pip:.2f} | {thd:.2f} | {regla['id']} {regla['resultado']} |"
        )
    lineas += [
        "",
        "</div>",
        "",
    ]
    lineas += [
        "",
        "## Estadísticas",
        "",
        "El punto de operación es uno por hoja. Con n = 1, mínimo, máximo, media y mediana coinciden con ese valor y la desviación estándar no se calcula.",
        "El archivo no se resume como un solo pozo.",
        "El survey sí tiene varias estaciones. Las cifras están en `data_procesados/estadisticas_survey.csv`.",
        "",
        "| Hoja | Estaciones | MD mínimo ft | MD máximo ft | Inclinación máxima deg |",
        "|---|---:|---:|---:|---:|",
    ]
    resumen = tabla_survey(estaciones)
    for hoja in hojas:
        md = next(f for f in resumen if f["hoja"] == hoja["hoja"] and f["variable"] == "md_ft")
        inc = next(f for f in resumen if f["hoja"] == hoja["hoja"] and f["variable"] == "inclinacion_deg")
        lineas.append(
            f"| {hoja['hoja']} | {md['n']} | {md['minimo']:.0f} | {md['maximo']:.0f} | {inc['maximo']:.1f} |"
        )
    lineas += [
        "",
        "No hay frecuencia de muestreo en el tiempo. El paso entre estaciones es de profundidad medida, no de días.",
        "No se armó una matriz de correlación: cinco puntos de operación de hojas distintas no estiman una relación causal, y mezclarlos sería tratarlos como un mismo pozo.",
        "",
        "## Gráficos",
        "",
        "![Caudal y límites por hoja](figuras/caudal_limites_por_hoja.png)",
        "",
        _texto_caudal(filas),
        "",
        "![Puntos de head a 60 Hz](figuras/head_puntos_60hz.png)",
        "",
        "Son los seis puntos escritos en la hoja. No se dibujó una curva de fabricante ni se marcó un BEP.",
        "",
        "![Survey MD y vertical por hoja](figuras/survey_md_tvd_por_hoja.png)",
        "",
        "Vertical es el número almacenado. No se recalculó la trayectoria.",
        "",
        "![Inclinación del survey](figuras/inclinacion_survey_por_hoja.png)",
        "",
        "La inclinación llega a valores cercanos a 90 grados en las cinco hojas. Cada caja es el survey de esa hoja.",
        "",
        "## Resultados de los cálculos",
        "",
        "En las cinco hojas el fluido y el balance quedan en estado calculable y el PIP y el THD coinciden con la caché.",
        "Eso comprueba la transcripción. La presión de sensor es una entrada, así que el PIP en pies no es una estimación sin sensor.",
        "No hay residual contra otra medición de PIP.",
        "",
        "## Capacidad predictiva",
        "",
        "Cálculo directo: gravedad, densidad, gradiente, PIP en pies, THP en pies, fricción y THD, con las fórmulas de la hoja.",
        "Estimación con parámetros no medidos en este libro: no se hizo. Faltan los coeficientes del Método B.",
        "Predicción de comportamiento futuro: no hay serie temporal ni variable objetivo de un instante posterior. No existe predicción validada.",
        "Sensibilidad local: sí se calculó, como derivada alrededor del punto escrito, no como un escenario de operación. Está más abajo.",
        "Simulación de un cambio de consigna: no se hizo y no se recomienda.",
        "",
        *_secciones_analiticas(hojas, filas),
        "",
        "## Pendientes",
        "",
        "- Quién confirma si la llave es Cluster o Pozo.",
        "- Unidad de BS&W y origen de las constantes de temperatura, de 0.052, de C = 120 y del exponente 4.8566.",
        "- Signo del PIP frente a F-12.",
        "- Si la tabla de seis puntos es de fabricante.",
        "- P-14, que no cambia este expediente y sigue sin respuesta.",
        "",
        "El expediente no pasa a `datasets/procesadas/` hasta que el usuario lo apruebe.",
        "",
    ]
    return "\n".join(lineas)


def _pip_cinco_pozos(hojas: list[dict]) -> str:
    """Diferencia celda menos hipótesis hidrostática. No cambia la fórmula."""
    partes = []
    for hoja in hojas:
        gradiente = gradiente_base(hoja)
        celda = pip_en_ft(hoja["presion_sensor_psi"], hoja["tvd_intake_ft"], hoja["tvd_sensor_ft"], gradiente)
        hidro = pip_ft_si_el_sensor_esta_mas_profundo(
            hoja["presion_sensor_psi"], hoja["tvd_intake_ft"], hoja["tvd_sensor_ft"], gradiente,
        )
        partes.append(f"{hoja['pozo']} {celda - hidro:.1f} ft")
    return (
        "En las cinco hojas el sensor está más profundo que el intake y la diferencia es el doble de esa separación: "
        + ", ".join(partes)
        + ". La caché coincide con la celda."
    )


def _exploratorio(hojas: list[dict]) -> list[str]:
    grupos: dict[str, list[str]] = {}
    for hoja in hojas:
        grupos.setdefault(str(hoja["bomba_referencia"]), []).append(hoja["pozo"])
    apis = {hoja["api_deg"] for hoja in hojas}
    lineas = [
        "## Los cinco puntos",
        "",
        "Cada hoja es un solo punto de operación. No hay serie temporal y las estaciones del survey no son ensayos de la bomba. "
        "Con cinco puntos heterogéneos no se estima una correlación ni un modelo estadístico.",
        "",
        "| Pozo | Hoja | Bomba escrita | Etapas | Hz | Caudal BFPD | P sensor psi | THP psi | ID in | TVD descarga ft |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for hoja in hojas:
        lineas.append(
            f"| {hoja['pozo']} | {hoja['hoja']} | {hoja['bomba_referencia']} | {hoja['etapas']:.0f} | "
            f"{hoja['frecuencia_hz']:.0f} | {hoja['caudal_operacion_bfpd']:.0f} | {hoja['presion_sensor_psi']:.0f} | "
            f"{hoja['thp_psi']:.0f} | {hoja['id_tubing_in']:.3f} | {hoja['tvd_descarga_ft']:.0f} |"
        )
    bombas = "; ".join(f"{nombre} en {', '.join(pozos)}" for nombre, pozos in grupos.items())
    lineas += [
        "",
        f"Hay dos textos de bomba, no cinco curvas distintas: {bombas}. "
        f"La frecuencia va de {min(h['frecuencia_hz'] for h in hojas):.0f} a {max(h['frecuencia_hz'] for h in hojas):.0f} Hz "
        f"y el caudal de {min(h['caudal_operacion_bfpd'] for h in hojas):.0f} a {max(h['caudal_operacion_bfpd'] for h in hojas):.0f} BFPD. "
        "El diámetro interno escrito es el mismo en las cinco hojas.",
        "",
        f"°API toma {len(apis)} valor distinto en las cinco hojas"
        + (f" ({next(iter(apis)):.0f}). Eso no prueba que el fluido sea el mismo en los cinco pozos: es la consulta CT-10." if len(apis) == 1 else "."),
        "Cada curva tabulada tiene seis puntos a 60 Hz. No son mediciones de la bomba en operación.",
        "",
        "## Qué relaciona el modelo",
        "",
        "El PIP en pies sale de la presión del sensor, las profundidades y el gradiente. No es una estimación sin sensor, y el signo es el de la celda (CT-03). "
        "Con el sensor más profundo que el intake, esa fórmula y una corrección hidrostática simple tienen signos opuestos; la transcripción no se reemplaza. "
        + _pip_cinco_pozos(hojas) + " "
        "La fricción de Hazen-Williams usa el caudal medido, el diámetro y la TVD de descarga como longitud, con el exponente 4.8566 de la hoja (CT-05). "
        "La THD suma esa fricción, la TVD de descarga y el THP en pies, y resta el PIP. "
        "Q* es el caudal en el que la altura de la bomba, llevada a la frecuencia de operación con las leyes de afinidad de la hoja y multiplicada por las etapas, iguala esa THD. "
        "Reproducir la caché de Excel demuestra la transcripción. No demuestra que el pozo vaya a producir Q*.",
        "",
    ]
    return lineas


def _sensibilidad(hojas: list[dict]) -> list[str]:
    """Elasticidad local de Q* para las diez entradas del cuaderno 04, más la derivada por pie de las TVD."""
    por_pozo: dict[str, dict[str, float]] = {}
    for hoja in hojas:
        por_pozo[hoja["pozo"]] = {}
        for clave in ENTRADAS_RELATIVAS:
            por_pozo[hoja["pozo"]][clave] = elasticidad_relativa(hoja, clave)["elasticidad"]
    ruta = figura_elasticidades(por_pozo, raiz_expediente() / "reports" / "figuras" / "elasticidad_q_estrella.png")
    pozos = [hoja["pozo"] for hoja in hojas]
    lineas = [
        "## Sensibilidad local",
        "",
        "La elasticidad es (ΔQ*/Q*) / (Δx/x), con diferencia central y un paso del 1 % en la entrada. "
        "Cada perturbación vuelve a calcular fluido, balance e intersección. "
        "El signo positivo quiere decir que, en este punto, Q* sube cuando sube esa entrada. "
        "La magnitud dice cuánto pesa la entrada aquí. No es una incertidumbre, no es un intervalo de confianza "
        "y no se extrapola a otra frecuencia o a otro pozo.",
        "",
        "| Entrada | " + " | ".join(pozos) + " |",
        "|---|" + "|".join("---:" for _ in pozos) + "|",
    ]
    medias = []
    for clave in ENTRADAS_RELATIVAS:
        valores = [por_pozo[pozo][clave] for pozo in pozos]
        medias.append((clave, sum(abs(v) for v in valores) / len(valores)))
        lineas.append("| " + clave + " | " + " | ".join(f"{v:.2f}" for v in valores) + " |")
    medias.sort(key=lambda par: par[1], reverse=True)
    lineas += [
        "",
        f"![Peso local de cada entrada](figuras/{ruta.name})",
        "",
        "En las cinco hojas la entrada de mayor |elasticidad| media es "
        f"`{medias[0][0]}` ({medias[0][1]:.2f}), seguida de `{medias[1][0]}` ({medias[1][1]:.2f}) y `{medias[2][0]}` ({medias[2][1]:.2f}). "
        "La frecuencia mueve Q* más que el caudal medido, el THP o el °API en este entorno. "
        "Eso describe el modelo transcrito. No autoriza a cambiar la frecuencia.",
        "",
        "Derivada de Q* respecto de la profundidad vertical de los equipos, en BFPD por pie, con un paso de 1 ft:",
        "",
        "| Pozo | " + " | ".join(TVD_EQUIPOS) + " |",
        "|---|" + "|".join("---:" for _ in TVD_EQUIPOS) + "|",
    ]
    for hoja in hojas:
        celdas = []
        for clave in TVD_EQUIPOS:
            derivada = derivada_por_pie(hoja, clave)
            celdas.append("—" if derivada is None else f"{derivada:.2f}")
        lineas.append("| " + hoja["pozo"] + " | " + " | ".join(celdas) + " |")
    lineas += [
        "",
        "Un pie más de profundidad no pesa igual en la descarga, en el intake y en el sensor, porque cada uno entra en un término distinto de la THD o del PIP.",
        "",
    ]
    return lineas


def _texto_caudal(filas) -> str:
    """Leyenda de la figura, calculada con la misma función que la tabla. No repite la clasificación vieja."""
    partes = []
    for hoja, _fluido, _balance, regla in filas:
        limites = limites_a_frecuencia(hoja)
        partes.append(
            f"{hoja['pozo']} ({hoja['hoja']}, {hoja['frecuencia_hz']:.0f} Hz): "
            f"caudal {hoja['caudal_operacion_bfpd']:.0f} BFPD, "
            f"máximo a esa frecuencia {limites['maximo_bfpd']:.0f} BFPD, "
            f"clasificación preliminar {regla['id']}."
        )
    hoja = next(t[0] for t in filas if t[0]["pozo"] == "QF-084")
    limites = limites_a_frecuencia(hoja)
    return (
        "Los círculos llenos son el máximo y el mínimo llevados a la frecuencia de operación (Q · f / 60). "
        "El círculo hueco es el máximo tal como está escrito a 60 Hz. "
        + " ".join(partes)
        + f" En QF-084 el máximo escrito a 60 Hz es {hoja['limite_maximo_bfpd']:.0f} BFPD y el caudal es "
        f"{hoja['caudal_operacion_bfpd']:.0f} BFPD a {hoja['frecuencia_hz']:.0f} Hz. "
        f"Escalado, el máximo es {limites['maximo_bfpd']:.0f} BFPD "
        f"({hoja['limite_maximo_bfpd']:.0f} × {hoja['frecuencia_hz']:.0f} / 60). "
        "El caudal queda dentro. Compararlo con el número de 60 Hz mezcla dos frecuencias y no es la clasificación vigente. "
        "El escalamiento no valida el límite del fabricante ni la afinidad (CT-08)."
    )


def _secciones_analiticas(hojas: list[dict], filas) -> list[str]:
    ids = [regla["id"] for *_resto, regla in filas]
    lineas = [
        "## Pregunta",
        "",
        "Qué se puede afirmar, con las cinco hojas, sobre el punto de operación escrito, "
        "y qué de eso puede consumir un evaluador de reglas sin tratarlo como una orden de operación.",
        "",
        *_exploratorio(hojas),
        "",
        "## Caudal calculado y caudal medido",
        "",
        "Q* es el caudal en el que la altura de la bomba, a la frecuencia de la hoja, iguala la THD. "
        "La THD usa el caudal medido en la fricción, así que el cálculo no es autoconsistente. "
        "La diferencia describe el contraste; no dice que el pozo pierda o gane producción.",
        "",
        "| Hoja | Pozo | Q medido BFPD | Q* BFPD | Diferencia relativa |",
        "|---|---|---:|---:|---:|",
    ]
    for hoja in hojas:
        cadena = calcular_hoja(hoja)
        q = cadena["q"].resultados["caudal_a_producir_bfpd"]["valor"]
        medido = hoja["caudal_operacion_bfpd"]
        lineas.append(
            f"| {hoja['hoja']} | {hoja['pozo']} | {medido:.0f} | {q:.0f} | {(q - medido) / medido:.1%} |"
        )
    lineas += [
        "",
        *_sensibilidad(hojas),
        "",
    ]
    fuera = dict(hojas[0])
    fuera["frecuencia_hz"] = 80.0
    q80 = calcular_hoja(fuera)["q"]
    valor80 = q80.resultados.get("caudal_a_producir_bfpd", {}).get("valor")
    lineas += [
        "",
        f"A 80 Hz, fuera del rango observado ({min(h['frecuencia_hz'] for h in hojas):.0f}–"
        f"{max(h['frecuencia_hz'] for h in hojas):.0f} Hz), la misma cadena sobre {hojas[0]['hoja']} "
        f"devuelve estado `{q80.estado}`"
        + (f" y {valor80:.0f} BFPD" if valor80 is not None else "")
        + f" con alertas {list(q80.alertas) or 'ninguna'}. "
        "El modelo no avisa de esa extrapolación. El evaluador del expediente sí la marca, sin cambiar la ecuación.",
        "",
        "## Reglas candidatas",
        "",
        f"Con los límites en la misma base de frecuencia, las cinco hojas dan {ids.count('RC-BES-03')} veces RC-BES-03, "
        f"{ids.count('RC-BES-01')} veces RC-BES-01 y {ids.count('RC-BES-02')} veces RC-BES-02. "
        "RC-BES-04 no se evalúa: no hay curva de fabricante ni una columna EFF de significado confirmado. "
        "Su consulta es CT-06. CT-09 es otra pregunta: qué diferencia entre Q* y el caudal medido se aceptaría, y no fundamenta el BEP.",
        "Ninguna regla está aprobada. El detalle está en `docs/reglas_candidatas.md` y el resultado estructurado sale de `evaluacion.motor.evaluar`.",
        "Una versión anterior de este informe decía que RC-BES-01 se activaba en QF-084. "
        "Eso correspondía a comparar el caudal a la frecuencia de operación con el máximo escrito a 60 Hz. "
        "Esa frase queda retirada. La comparación sin escalar se conserva en el código solo como control del artefacto.",
        "",
        "## Hallazgos",
        "",
        "Cinco puntos no alcanzan para una correlación. Lo que sí se puede decir, y lo que no:",
        "",
        "- Hay dos textos de bomba, no cinco curvas de fabricante. Compartir el rótulo S 8000N o S6000N no demuestra que la máquina sea la misma.",
        "- En la misma base de frecuencia, el caudal escrito queda entre el mínimo y el máximo escalados en las cinco hojas. La clasificación preliminar es RC-BES-03. Eso es coherencia con los números de la hoja, no un aval de operación.",
        "- Q* y el caudal medido no coinciden. El caudal medido entra en la fricción, así que el contraste no es una validación predictiva independiente.",
        "- La elasticidad local de mayor |media| es la frecuencia. Describe el modelo transcrito alrededor de cada punto. No es una incertidumbre y no autoriza a mover la frecuencia.",
        "- RC-BES-04 no se evalúa. La columna EFF no tiene un significado físico confirmado. La consulta que lo bloquea es CT-06, no la tolerancia entre Q* y el caudal medido.",
        "",
        "## Qué puede usar la aplicación",
        "",
        "Los resultados que pueden alimentar una regla son los que el motor ya calcula y deja en evidencia: caudal de operación, frecuencia, límites escritos, límites escalados con Q ∝ f, PIP, THD y Q*. "
        f"Los modelos implementados, versión de transcripción, son {', '.join('`' + m['id'] + '`' for m in MODELOS)}. "
        "Para evaluar una hoja hacen falta las variables de fluido, de balance y de la curva: °API, temperatura, BS&W, presión de sensor, THP, las tres TVD, caudal, diámetro, frecuencia, etapas y los límites a 60 Hz, cada una con su unidad.",
        "",
        "Reglas formuladas: " + ", ".join(r["id"] for r in REGLAS) + ". "
        "Ejecutables como evaluación preliminar, todavía sin aprobación: "
        + ", ".join(r["id"] for r in REGLAS if r["estado_validacion"] == "pendiente_validacion") + ". "
        "Bloqueadas: " + ", ".join(
            f"{r['id']} ({', '.join(r['consultas_tecnicas']) or 'sin consulta'})" for r in REGLAS if r["estado_validacion"] == "no_evaluable"
        ) + ". "
        "CT-06 impide tratar la tabla EFF como curva de fabricante. CT-08 impide aprobar el escalamiento de los límites. CT-09 impide llamar validación al contraste entre Q* y el caudal medido.",
        "",
        "La aplicación envía mediciones, no la ficha: los límites, las etapas y la curva no se sustituyen en el modo operacional. Una variable repetida se rechaza. "
        "Reproducir la caché de Excel demuestra la transcripción de las fórmulas, no su validez física. "
        "La aplicación debe conservar el identificador y la versión de cada regla, el identificador de cada modelo, la evidencia numérica, las limitaciones y el estado `recomendacion_operacional_autorizada`. "
        "Un modelo de lenguaje, más adelante, solo podrá redactar ese resultado. No calcula, no aprueba reglas y no indica cambios de frecuencia.",
        "",
        "## Conclusiones",
        "",
        "El código reproduce la cadena escrita en las cinco hojas y distingue un caudal dentro de los límites escalados de una comparación entre frecuencias distintas. "
        "La diferencia entre el PIP de la celda y la corrección hidrostática simple está cuantificada en las cinco hojas y no se corrigió la fórmula. "
        "El catastro de fórmulas, con las cantidades contadas desde el inventario, está en docs/catastro_maestro_formulas_BES-jun.md. "
        "Una curva de simulación tiene que traer el caudal estrictamente creciente en el orden enviado; no se reordena. "
        "No queda validada la física de esas fórmulas: el signo del PIP, el exponente de Hazen-Williams, la unidad de BS&W, la identidad Cluster/Pozo y el origen de los límites siguen abiertos. "
        "Por eso el expediente permanece en `en_uso`, en estado de validación pendiente, y ninguna salida de este informe es una instrucción de operación.",
        "",
    ]
    return lineas


def _html_despues(_hojas) -> str:
    return ""


def main() -> None:
    markdown, _html = construir()
    raiz = raiz_expediente()
    ruta_md = raiz / "reports" / "informe_analisis_BES-jun.md"
    ruta_md.write_text(markdown, encoding="utf-8")
    print(ruta_md)


if __name__ == "__main__":
    main()
