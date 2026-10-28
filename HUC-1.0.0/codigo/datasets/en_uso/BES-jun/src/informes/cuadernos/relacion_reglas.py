"""Qué aporta cada cuaderno al motor de reglas. No convierte un inventario en una regla."""

RELACION = {
    "00_inventario_y_fuentes": (
        "Este cuaderno no produce parámetros para el motor. Comprueba que la copia de trabajo es el mismo archivo "
        "que se analizó. Sin esa identidad, `integracion/manifiesto.json` no tendría una huella que citar."
    ),
    "00_inventario_y_trazabilidad": (
        "Tampoco formula reglas. Deja escrito cómo se relacionan los doce cuadernos y qué archivo produce cada uno. "
        "El motor no lo ejecuta."
    ),
    "01_inspeccion_BES_jun": (
        "Identifica hoja, Cluster, Pozo, bomba, frecuencia, caudal y límites escritos. "
        "Esos campos alimentan `integracion/pozos.json`. La identidad queda provisional: el motor resuelve la hoja "
        "dentro de este archivo y no declara una llave global. Unidad de almacenamiento: la del rótulo, sin convertir. "
        "Confianza: alta como lectura de la celda, baja como identificador de pozo."
    ),
    "01_inspeccion_y_calidad_datos": (
        "Dictamina qué defectos contaminan el cálculo y cuáles no. No crea umbrales. "
        "El motor usa esa distinción cuando un dato falta o cuando BS&W sale de 0 a 1: advierte, no inventa el valor."
    ),
    "02_ecuaciones_y_variables": (
        "Documenta las diez ecuaciones que los modelos transcriben, con unidad, hipótesis y función de Python. "
        "No las aprueba. El catálogo `analisis.catalogo_bes_jun` es el que el informe y la ficha citan."
    ),
    "02_trazabilidad_y_analisis_formulas": (
        "Clasifica cada fórmula como utilizable, utilizable con reserva o fuera de alcance, y enlaza la reserva con una CT. "
        "El motor puede calcular una fórmula «con reserva»; el resultado sigue siendo preliminar."
    ),
    "03_limpieza_y_mapeo": (
        "Fija el nombre y la unidad con los que cada variable se guarda, y demuestra que el valor no se alteró al mapearlo. "
        "Ese nombre canónico es el de `integracion/variables.json`. No define límites de operación."
    ),
    "03_mapeo_y_preparacion_BES_jun": (
        "Prepara la curva de seis puntos que consume `M-BES-INTERSECCION`. "
        "La curva es una tabla escrita a 60 Hz, no una serie de ensayos. Unidad: BFPD y ft, como en la hoja."
    ),
    "04_calculos_deterministicos": (
        "Ejecuta la cadena y contrasta cada magnitud intermedia con la caché. "
        "Produce PIP, THD y el caudal a producir, con unidad y fórmula. "
        "La ficha de confiabilidad de este cuaderno dice para qué no sirven: el motor repite esa barrera "
        "con `recomendacion_operacional_autorizada = false`."
    ),
    "04_modelo_deterministico": (
        "Mide la sensibilidad de Q* y muestra que a 80 Hz, fuera del rango observado, el modelo calcula sin avisar. "
        "El evaluador añade esa advertencia en la capa de reglas. No se cambió la ecuación para que el aviso apareciera dentro del modelo."
    ),
    "05_evaluacion_por_pozo": (
        "Produce la evidencia de la ventana de caudal. Parámetro: caudal de operación (BFPD) frente a los límites escritos "
        "escalados con f/60. La regla que depende de él es RC-BES-03 en las cinco hojas. "
        "RC-BES-01 sin escalar queda como artefacto, no como resultado. Confianza baja. CT-08 sigue abierta."
    ),
    "06_hallazgos_y_reglas_candidatas": (
        "Es la especificación que `reglas.catalogo` y `reglas.candidatas_bes_jun` implementan. "
        "Estado de las cuatro reglas: pendiente o no evaluable. Ninguna aprobada. "
        "El motor no añade reglas que este cuaderno no haya dejado escritas."
    ),
}
