"""Limitaciones y referencias de cada cuaderno (se añaden al final por ``base.guardar``).

Las referencias son solo las fuentes realmente consultadas por el cuaderno. No se cita literatura que no
esté en el proyecto: donde un método es de uso general (curvatura mínima, Hazen-Williams, leyes de afinidad)
se dice expresamente que no hay una cita verificada en las fuentes del expediente.
"""

REF = {
    "libro": "**Libro de trabajo:** `entrada/BES_jun.xlsx`, copia byte a byte de «Copia de FINAL BES-jun.xlsx» (SHA-256 `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`). Cinco hojas: QF-554H, QF-545H, QF-500H, QF-378HST y QF-549HST.",
    "pdf004": "**`004-ESPdesign.pdf`** (en la raíz del proyecto): se consultó solo para el exponente de fricción 4.8655 y para el significado de TDH (CT-05).",
    "e1": "**`Modelo_Sensorless_PIP_ESP_Set_Ecuaciones.docx`** (raíz del proyecto): se consultó solo para la analogía de la corrección de PIP (F-12) usada en la sensibilidad CT-03. No es la fórmula de la hoja.",
    "xlsm": "**`Copia de Copia de Ecuaciones  _.xlsm`** (raíz del proyecto): fuente de F-01 (gravedad específica) y del gradiente 0.433, leída sin ejecutar macros.",
    "inv": "**`docs/inventario_fuentes.md`** (raíz del proyecto): registro de huellas de las fuentes en la fecha del inventario.",
    "ct": "**`docs/consultas_tecnicas_pendientes.md`** (expediente): registro CT-01…CT-10 de ambigüedades abiertas.",
    "plan": "**`trabajo.md` y `trabajo2.md`** (raíz del proyecto): plan de trabajo, reglas de no mezclar libros y bloqueo P-14.",
    "sw": "**Software:** Python 3.14.8, pandas 3.0.6, numpy 2.5.4, matplotlib 3.11.2, openpyxl 3.1.5 (versiones tomadas de la ficha de entorno de cada ejecución).",
    "gen": "**Métodos de uso general sin cita verificada en las fuentes del expediente:** {texto}. Se aplican como están escritos en la hoja o se describen como método estándar, sin atribuirlos a un texto concreto.",
}


def _ref(*claves, gen=None):
    items = [REF[c] for c in claves if c != "gen"]
    if gen:
        items.append(REF["gen"].format(texto=gen))
    return "\n".join(f"{i}. {t}" for i, t in enumerate(items, 1))


CIERRES = {
    "00_inventario_y_fuentes": (
        "- La huella SHA-256 demuestra **identidad binaria**, no que el contenido del libro sea correcto.\n- El inventario de fuentes registra huellas de una fecha; si el documento de inventario estuviera mal, el contraste lo heredaría.\n- Los archivos `RB-*` solo se contrastan con `os.stat` (tamaño y fecha): **no se abren** por la regla del expediente.\n- La ficha `dataset.md` es un documento humano: se contrasta, no se da por cierta.",
        _ref("libro", "inv", "plan", "sw"),
    ),
    "00_inventario_y_trazabilidad": (
        "- El **linaje** (qué cuaderno escribe qué archivo) está **declarado** en una tabla del propio cuaderno; el control verifica existencia y huella, no que el cuaderno indicado haya sido el productor.\n- El estado de ejecución se lee de los `.ipynb` guardados en disco, no de una ejecución en vivo; este mismo cuaderno se omite de esa lectura.\n- Las huellas de los originales respaldados prueban que no han cambiado desde el respaldo, no que fueran correctos antes.\n- No hay control de versiones Git en el proyecto: el diff se hace contra el respaldo con manifiesto.",
        _ref("libro", "plan", "sw"),
    ),
    "01_inspeccion_BES_jun": (
        "- La inspección describe una **instantánea** del libro; no es una serie temporal (cuaderno 01).\n- La ubicación de cada bloque se halla por **rótulo**; si alguien renombrara un rótulo, la búsqueda fallaría de forma visible, pero no se detectaría un rótulo que cambiara de significado.\n- Las figuras del survey son descriptivas; no verifican que el survey corresponda al pozo real.\n- Solo se inspeccionan las cinco hojas del libro activo.",
        _ref("libro", "sw", gen="curvatura mínima para trayectorias de pozo (mencionada, no desarrollada aquí)"),
    ),
    "01_inspeccion_y_calidad_datos": (
        "- La calidad se mide con controles **propios** (tolerancias, plausibilidad física, curvatura mínima): son criterios del expediente, no normas.\n- La curvatura mínima es un control **independiente** de las columnas del survey, no un reemplazo: una desviación indica inconsistencia, no cuál de los dos es el correcto.\n- Una hoja sin hallazgos significa «sin hallazgos con estos controles».\n- El rastreo de precedentes resuelve referencias A1 de la misma hoja; una referencia dinámica (INDIRECT, OFFSET) no se seguiría (no hay en la cadena).",
        _ref("libro", "sw", gen="curvatura mínima (control de survey) y relación hidrostática P = ρ·g·h"),
    ),
    "02_ecuaciones_y_variables": (
        "- Cada ecuación es una **transcripción** de lo que escribe la hoja; que el código la reproduzca no la valida físicamente.\n- La categoría asignada (documentada, implementada, empírica, hipótesis) refleja la evidencia disponible; podría cambiar si aparece un origen para una constante.\n- Las comprobaciones de límite (escalado de la fricción, afinidad) prueban propiedades matemáticas de la fórmula, no su ajuste a una bomba real.\n- Los dominios de validez declarados son los de la propia fórmula; no se tiene un rango de validez de fabricante.",
        _ref("libro", "pdf004", "e1", "xlsm", "ct", "sw", gen="Hazen-Williams para fricción en tubería y leyes de afinidad de bombas centrífugas"),
    ),
    "02_trazabilidad_y_analisis_formulas": (
        "- La firma estructural prueba que las fórmulas son **iguales entre hojas**, no que sean correctas.\n- El análisis dimensional de rótulos depende de cómo los escribió quien armó el libro (hay grafías distintas de la misma unidad).\n- El argumento hidrostático sobre CT-03 es de **signo**, no de magnitud, y asume fluido de gradiente constante.\n- El catálogo de fórmulas es una clasificación de este expediente; no es una aprobación (puerta G1).",
        _ref("libro", "pdf004", "e1", "xlsm", "ct", "sw", gen="presión hidrostática y análisis dimensional"),
    ),
    "03_limpieza_y_mapeo": (
        "- El mapeo localiza celdas por rótulo y valida con una prueba de ida y vuelta; no corrige rótulos incorrectos (los registra).\n- No se convierten unidades ni se imputan datos: la tabla es tan buena como el libro.\n- La tabla larga contiene 34 variables elegidas por su uso en el cálculo; otras celdas del libro no se mapean.\n- Los parámetros idénticos entre hojas se señalan; si son datos de plantilla o de pozo no puede decidirse con el libro (CT-10).",
        _ref("libro", "ct", "sw"),
    ),
    "03_mapeo_y_preparacion_BES_jun": (
        "- Las tablas ordenadas (survey y curvas de bomba) son copias fieles; las estadísticas son **descriptivas** con n = 5 hojas y 6 puntos por curva.\n- No se eliminan valores atípicos ni se rellenan faltantes.\n- Las curvas de bomba están repetidas entre pozos (hallazgo H-09); la estadística por pozo no equivale a una caracterización de cada bomba.\n- Los gráficos usan la escala natural de cada variable y no se comparan entre sí.",
        _ref("libro", "ct", "sw"),
    ),
    "04_calculos_deterministicos": (
        "- Reproducir la hoja no es validarla: el código y la hoja comparten fórmulas.\n- Los casos límite prueban que el código **se niega** a calcular fuera de dominio, no que el dominio sea el físicamente correcto.\n- La ficha de confiabilidad es un juicio de este expediente (reservas CT), no una certificación.\n- Los resultados dependen del signo de PIP (CT-03) y del exponente (CT-05).",
        _ref("libro", "pdf004", "ct", "sw"),
    ),
    "04_modelo_deterministico": (
        "- Las sensibilidades son **locales** (diferencia finita de ±1 % alrededor del punto de operación de cada hoja); no extrapolan a otros puntos.\n- No se conoce la incertidumbre real de cada entrada, por lo que las elasticidades indican **cuánto pesa** cada una y no cuánto se equivoca el resultado.\n- El dominio de validez es el observado en cinco hojas; salir de él es extrapolar.\n- Es un modelo transcrito: no se ajusta ni se calibra.",
        _ref("libro", "pdf004", "ct", "sw", gen="diferencias finitas centrales para sensibilidad local"),
    ),
    "05_evaluacion_por_pozo": (
        "- Con n = 5 hojas (un punto por pozo) todo contraste es **descriptivo**; no hay inferencia estadística.\n- El caudal medido no es independiente del cálculo (entra en la fricción) y el PIP parte de la presión del sensor.\n- La ventana operativa usa límites escritos en la hoja, no de fabricante, y supone Q ∝ f.\n- La sensibilidad cambia una ambigüedad cada vez; no explora combinaciones.",
        _ref("libro", "pdf004", "e1", "ct", "sw", gen="leyes de afinidad de bombas centrífugas"),
    ),
    "06_hallazgos_y_reglas_candidatas": (
        "- Los hallazgos son los que detectan los controles de los cuadernos 00–05; no es una auditoría exhaustiva del libro.\n- Las reglas candidatas usan umbrales **escritos en la hoja**; ninguna está aprobada ni respaldada por fabricante.\n- La prioridad de cada hallazgo es un criterio de este expediente (efecto en el cálculo y posibilidad de resolverlo con los datos).\n- La tabla de afirmaciones es la frontera del expediente: afirmar fuera de ella exige resolver las consultas.",
        _ref("libro", "pdf004", "e1", "ct", "plan", "sw"),
    ),
}
