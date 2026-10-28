# Discrepancias científicas · BES-jun

Clasificación al 2026-10-20. No se modificó una ecuación para obtener otra salida.

| Tema | Clase | Qué se hizo |
|---|---|---|
| QF-084 y el máximo de caudal | Error confirmado en el informe y en la ficha de reglas, no en el cálculo | El código ya escalaba. Se corrigió el texto y se añadió una prueba de regresión. |
| Signo del PIP frente a la hidrostática | Ambigüedad técnica (CT-03) | Se conserva el signo de la hoja. |
| Exponente 4.8566 de la hoja y 4.8655 del PDF | Inconsistencia documental (CT-05) | Se usa el de la hoja. No se sustituyó. |
| Longitud de fricción = TVD de descarga | Hipótesis no validada | Se transcribe lo que la celda hace. |
| La fricción usa el caudal medido para calcular el caudal resultante | Hallazgo estructural | Documentado. No se iteró a punto fijo como si fuera la corrección. |
| Frecuencias de límites y de operación | Error de la primera comparación, ya corregido en código | La comparación vigente usa la misma base. `escalar=False` solo reproduce el artefacto. |
| BS&W rotulado % y usado como fracción | Ambigüedad técnica (CT-02) | El modelo advierte si el número está fuera de 0 a 1. |
| Columna EFF y «Cono de eficiencia» | Pendiente de aprobación externa (CT-06) | RC-BES-04 queda `no_evaluable`. CT-09 es la tolerancia entre caudal calculado y medido, no esta regla. |
| Procedencia de «Limite maximo» y «Limite minimo» | Pendiente de aprobación externa (CT-06, CT-08) | Se evalúan como coherencia con el texto de la hoja, no como límite de seguridad. |
| Hoja, Cluster y Pozo | Ambigüedad técnica | Identidad provisional. El motor no elige una llave global. |
| Valores cacheados | Limitación de los datos | El contraste es contra la caché del mismo libro, no contra otra medición. |
| `=TODAY()` y la fecha de 2017 en QF-549HST | Limitación de los datos | No se usan como fecha histórica de operación. |
| Extrapolación a 80 Hz sin alerta dentro del modelo | Limitación conocida | No se cambió el modelo. El evaluador sí advierte si la frecuencia sale del rango observado. |
