# Consola operacional ESP

## Qué pregunta la pantalla

La consola responde tres cosas, y solo con lo que el expediente puede sostener:

1. Cómo queda el pozo elegido con los datos que ya están en su ficha.
2. Qué recalcula el motor si se cambia la frecuencia o la TVD de admisión en un escenario hipotético.
3. Qué puede decirse ante una condición preliminar, y qué no puede decirse mientras no exista un límite crítico validado.

No dice si Ollama está conectado. Eso quedó en Configuración de IA. El menú lateral lista los pozos de la ficha con una luz del escenario inicial, o de la simulación de esta sesión si se movió un mando. El gris no es una falla de la bomba.

## Del selector al primer estado

1. `GET /` pinta el selector con los `pozo_rotulo` de `integracion/pozos.json`. Hoy son QF-084, QF-301, QF-147, QF-005 y QF-306, cada uno con su hoja y la bomba escrita (S 8000N o S6000N). RB-1521 y RB-IA-2191 no entran: no tienen pozos en un paquete de integración.
2. Al elegir un pozo, el navegador llama `GET /api/consola/pozos/<id>/escenario/`.
3. El servicio lee `condiciones_registradas.frecuencia_hz`, `profundidades_ft.tvd_intake`, el sensor, la descarga y el caudal registrado. Si un número no está, el mando queda inhabilitado y el valor es «No disponible». No se rellena con cero.
4. La leyenda es siempre la de escenario inicial sin telemetría. `fecha_medicion` es null. No se toma la última fila de un CSV como «ahora».
5. El navegador envía esos valores a `POST /api/consola/pozos/<id>/evaluar/`. Si coinciden con la ficha, la solicitud al motor va sin sustituciones, en modo operacional. El motor lee la hoja.
6. `estado_operacional.clasificar` mira `estado_evaluacion`, las reglas activas, `aprobada_para_uso_operacional`, `limite_critico_validado` y `recomendacion_operacional_autorizada`.
7. Para QF-084 sin cambios el motor termina en `completada_preliminar`, activa RC-BES-03 y no aprueba la regla. El rótulo es **SIN CLASIFICACIÓN OPERACIONAL**. La lámpara es gris. Estar entre los límites escritos no es NORMAL: la regla no está aprobada y `recomendacion_operacional_autorizada` queda en falso.
8. En la misma respuesta viajan PIP, THD y el caudal de intersección, con unidad y origen «calculado». El PIP lleva la nota de CT-03. La potencia no trae número.

## Qué pasa al mover un mando

El deslizador y el número se actualizan al instante. El número visible usa como máximo dos decimales; el valor enviado al motor conserva la precisión de la ficha. A los 300 ms, si el operador no siguió moviendo, el cliente incrementa `evaluacion_id`, aborta la petición anterior y envía el escenario. La pantalla pasa antes a «EVALUANDO» y no deja el color del escenario previo.

- Frecuencia distinta: entra en `variables` con unidad Hz y procedencia `operador`. Como hay un cambio, la solicitud completa va en `modo=simulacion` con `escenario_id`.
- TVD de admisión distinta: es un parámetro protegido. Solo puede ir en `parametros_escenario` como `{valor, unidad: "ft"}` y obliga el modo simulación. El motor copia el valor sobre una copia de la hoja en memoria. No guarda el libro.
- Potencia o head: la API responde 400. No llegan al motor.
- Frecuencia menor o igual que cero, un texto, o una unidad que no es la canónica: 400. No se convierte en cero.

La pantalla pasa a «Evaluando escenario...» hasta que vuelve el cálculo. Si llega una respuesta con otro `evaluacion_id`, el cliente no la pinta.

Ejemplo verificado en QF-084: a 63 Hz la regla activa es RC-BES-03 (10301 BFPD está entre los límites escritos escalados; el máximo escalado es 10500). El rótulo es SIN CLASIFICACIÓN OPERACIONAL. A 60 Hz el máximo escrito queda en 10000 y se activa RC-BES-01. Eso es INCIPIENTE, no CRÍTICO: el máximo escrito no está marcado como límite crítico validado. El texto dice que no se aplique el escenario a la bomba real. No se fabricó un umbral para pintar de verde ni de rojo.

Mover la admisión de QF-084 a 2700 ft cambia el PIP que devuelve el balance, porque la celda depende de esa TVD. El sensor no se mueve. La nota recuerda que el signo físico sigue abierto. El Excel no cambia de huella.

«Inicio» devuelve un solo parámetro a su valor de ficha y evalúa. «Restaurar valores» hace lo mismo con todos. La línea fija sigue diciendo que la simulación no se aplica al pozo real. No hay botón «Evaluar escenario»: el cálculo sale al cambiar un mando.

## Qué hace Ollama y qué no

Después del cálculo, el cliente pide otra vez el mismo escenario con `explicar: true`. El servidor vuelve a ejecutar el motor, clasifica otra vez y solo entonces llama a `/api/chat`. El prompt dice el rótulo ya decidido y prohíbe cambiarlo.

La acción recomendada de la pantalla es siempre la determinística. Si el modelo no responde, responde vacío, se corta por longitud o llama a la bomba normal, incipiente o crítica cuando ese no es el rótulo, se descarta su texto y queda el mensaje de respaldo. Si el asistente no está disponible, se añade esa frase y se conserva la clasificación física, cuando existe. Un fallo de cálculo no se pinta como estado de la bomba. El nombre del modelo, los tokens y el razonamiento interno no se escriben en esta página.

## Recorrido de los mandos

No hay en el expediente un límite de variador ni de motor. El deslizador de frecuencia recorre del 50 % al 150 % del valor de esa hoja, y el de TVD ±100 ft. La ficha del mando dice que eso no es un límite del equipo. Un número escrito a mano puede salir de ese recorrido; el motor avisará si la frecuencia sale del dominio observado (56 Hz a 67 Hz en estas cinco hojas) y seguirá sin tratarlo como límite autorizado.

## Dónde quedó la administración

`/administracion/` muestra el registro, Ollama y los conteos. Datasets, evaluaciones, asistente y configuración conservan sus URL. La consola no las repite.
