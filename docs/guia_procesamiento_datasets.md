# Guía de procesamiento de datasets

Metodología común del proyecto HUC. BES-jun es el primer caso, no un molde rígido: otro archivo puede tener otras variables, otra física y menos cuadernos. No se copian sus ecuaciones a un dataset cuya documentación no las respalde.

Los datasets en `en_espera` no se analizan hasta que se autorice el inicio. Hoy están RB-1521 y RB-IA-2191. No se abren en una pasada dedicada a otro expediente.

## Recibir y registrar

1. Anotar el nombre del archivo, quién lo entregó y la fecha. No renombrar el original en `fuentes/originales/`.
2. Calcular SHA-256 y tamaño sin modificar el archivo.
3. Dejarlo en `datasets/en_espera/<id>/`. Estado: `pendiente`.
4. No mezclar sus filas con las de otro libro.

## Autorizar el análisis

5. Confirmar que no es un duplicado de un expediente ya abierto (huella distinta).
6. Solo entonces copiar el trabajo a `datasets/en_uso/<id>/` y crear `entrada/` como copia de cálculo. El original sigue intacto. Estado: `inventariado` y, al empezar, `en_analisis`.

## Analizar

7. Identificar hojas, pozos y unidades con lo que el archivo dice. Si hay dos códigos y el libro no elige la llave, la identidad queda provisional.
8. Escribir la Ficha Maestra con los números que salen del código, no de una tabla pegada a mano.
9. Elegir los análisis que el archivo permite. Un punto por pozo no justifica un modelo estadístico ni aprendizaje automático. Conservar las etapas (integridad, calidad, ecuaciones, cálculo, evaluación, hallazgos), no el número de cuadernos de BES-jun.
10. Transcribir solo ecuaciones que el archivo o su documentación escriben. Si hay un error conocido, dejar la réplica identificada y la alternativa como pendiente de aprobación. No cambiar la física para que una prueba quede más cómoda.
11. Registrar hallazgos con la evidencia que los produce.
12. Formular reglas con umbral, unidad, procedencia y estado. Un número escrito en la hoja no es un límite de seguridad aprobado.
13. Una regla nace `candidata` o `pendiente_validacion`. Pasa a `aprobada` solo con responsable y fecha. Si falta información, el estado es `no_evaluable`, no un sí ni un no.
14. Armar el paquete de integración: manifiesto, pozos, variables, modelos, reglas, contratos y una guía que alguien que no hizo el análisis pueda seguir. El motor se ejecuta sin un modelo de lenguaje.
15. Separar mediciones del operador y parámetros de la ficha. En el modo ordinario una medición no reescribe límites, curvas ni geometría. Una variable repetida rechaza la solicitud; no se conserva el último valor. Un escenario hipotético lleva identificador propio, no actualiza la ficha y no autoriza operación. Los nombres protegidos son de cada dataset: BES-jun no los impone a otro archivo.

## Cerrar documentos y pruebas

16. HTML y PDF salen del documento completo (cuaderno → HTML → PDF; Markdown del informe → HTML → PDF). No de un resumen escrito aparte.
17. Ejecutar el AutoTest del expediente. En BES-jun: `python -m evaluacion.autotest` desde su raíz, con `PYTHONPATH=src`.
18. El informe consolidado lee los resultados vigentes. Un reporte de una corrida anterior se marca como histórico si se conserva.
19. Comprobar el cierre con el módulo de promoción del expediente. En BES-jun: `ciclo.promocion.comprobar`. El estado puede quedar en `validacion_pendiente` aunque el código termine sin errores.
20. Pedir autorización explícita para mover la carpeta. El código de BES-jun no mueve el expediente aunque se le pida.
21. Tras esa autorización, y no antes, una persona mueve `datasets/en_uso/<id>/` a `datasets/procesadas/<id>/`. Estado: `procesado`. Si una consulta bloquea el análisis, el estado es `bloqueado` y el dataset no se mueve.

## Qué es común y qué es propio del archivo

Común: integridad, inventario, perfil, diccionario, identidad de pozo, hallazgos, forma de una regla, separación entre medición y ficha, contratos de entrada y salida, pruebas, guía de integración, exportación y estados.

Propio: el lector del formato, las variables, las ecuaciones, las curvas, los parámetros y las reglas de ese archivo.
