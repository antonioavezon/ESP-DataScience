# Transiciones de estado de la consola

Decisión de software de esta versión, pendiente de validación técnica. No cambia el motor ni `recomendacion_operacional_autorizada`, que sigue en falso.

## Política de agregación

`comparar_caudal_con_limites` devuelve una sola observación entre RC-BES-01, RC-BES-02 y RC-BES-03. RC-BES-04 no se activa. La lámpara sigue esa observación.

Si en una respuesta sintética hubiera a la vez una regla con `aprobada_para_uso_operacional` y `limite_critico_validado`, esa gana y el estado es CRÍTICO. BES-jun no produce ese caso. La prueba que lo usa está marcada como diccionario sintético, no como pozo.

No se declara NORMAL porque el cálculo haya terminado. Se declara NORMAL solo si RC-BES-03 está activa: el caudal registrado está entre el mínimo y el máximo escritos, inclusive, a la frecuencia del escenario.

## Qué estado existe

| Estado | Cuándo | Color |
|---|---|---|
| NORMAL | RC-BES-03 activa | Verde |
| INCIPIENTE | RC-BES-01 o RC-BES-02 activa | Amarillo |
| CRÍTICO | Solo una regla aprobada y marcada como límite crítico validado | Rojo |
| Evaluación no disponible | Faltan datos, el cálculo falla, o no hay regla de caudal | Gris. No es un estado de la bomba |

No hay rótulo «SIN CLASIFICACIÓN OPERACIONAL». Con la medición registrada, los cinco pozos quedan en NORMAL porque el caudal está dentro de los límites escalados.

No hay tres zonas en la regla real. El único corte es el mínimo escrito y el máximo escrito. Por encima o por debajo es INCIPIENTE, no CRÍTICO: el catálogo no marca ese límite como crítico y la regla está en `pendiente_validacion`. No se inventó un segundo umbral.

El borde es inclusive. En QF-084, a 63 Hz, el máximo escalado es 10 500 BFPD. 10 500 queda en NORMAL. 10 501 queda en INCIPIENTE. Al volver a 10 301 BFPD, que es la medición de la hoja, regresa a NORMAL.

Bajar la frecuencia de QF-084 a 60 Hz deja el máximo escrito en 10 000 BFPD. El caudal de 10 301 lo supera y la lámpara pasa a INCIPIENTE por RC-BES-01. Volver a 63 Hz regresa a NORMAL.

## Qué no se puede calcular

CRÍTICO no sale de ningún pozo de BES-jun. Falta un límite crítico validado y una regla aprobada. RC-BES-04 no clasifica. CT-08 y CT-06 siguen abiertas: la comparación usa la afinidad de la hoja, y eso no valida el límite del fabricante.

La frecuencia fuera del intervalo 56–67 Hz no es, por sí sola, un color. Si la regla de caudal igual se evalúa, manda esa regla.

## Pantalla

El texto del operador dice si el caudal está entre los límites o si los supera o queda por debajo. No dice que la bomba esté autorizada. Ollama recibe el rótulo, la regla activa y los valores ya calculados. Si contradice el rótulo, o si no responde, queda el texto determinístico.
