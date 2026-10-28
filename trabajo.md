# Plan de trabajo para un asesor operacional VESP y ESP

**Propósito:** guiar el trabajo en Cursor desde el aprendizaje del sistema de bombeo electrosumergible hasta un prototipo que convierta los datos recibidos y los resultados de un modelo determinístico en explicaciones claras para un operador.  
**Estado inicial:** alcance educativo y de prototipo acordado; ejecución técnica pendiente.  
**Fecha:** 17 de octubre de 2026.

## Decisión de esta iteración (2026-10-17)

El archivo leído en esta iteración es `Copia de FINAL BES-jun.xlsx`. No sustituye a `RB-1521-PY-121120.xls` ni a `RB-IA-2191-Data.xlsx`. Esos dos libros quedan para etapas posteriores y sus filas no se mezclan con BES-jun. BES-jun no se incorpora al tablero de `asesor-esp` mientras P-14 no tenga respuesta.

`trabajo2.md` y `asesor-esp/trabajo.md` son el mismo plan (MD5 `f6a883a720ad3f4da07ab45363dc5522`). Ese plan llama D1 a RB-1521 y deja abierta la pregunta P-12 porque D1 tiene un solo pozo. Si BES-jun responde esa pregunta, o si entra al tablero, lo decide el responsable del alcance en P-14. El registro está en `docs/decisiones_pendientes.md`.

## Bloqueo del motor determinístico general (2026-10-17)

El motor determinístico general está **bloqueado** hasta que se cumplan las dos condiciones:

1. P-14 tiene respuesta documentada: texto, fecha, responsable y efecto en el orden de procesamiento, en `docs/decisiones_pendientes.md`. Hoy la respuesta está vacía. El orden del tablero sigue siendo D1 y después D2.
2. La puerta de fórmulas está revisada: las ecuaciones de los documentos y las fórmulas del XLSM están trazadas y reconciliadas; la formulación base tiene unidades, supuestos, dominio de uso y parámetros requeridos; las diferencias y los faltantes están documentados. Hoy `docs/decision_modelo_base.md` es borrador y G1 no está aprobada.

P-14 no impide el análisis aislado de BES-jun. Ese análisis no lo incorpora al tablero.

La unidad de trabajo pasa a ser un expediente por Excel, en `datasets/en_uso/`, `datasets/en_espera/` y `datasets/procesadas/`. Solo hay un expediente en uso: `datasets/en_uso/BES-jun`, en estado **Listo para revisión**. No se mueve a `procesadas/` ni se activa el siguiente hasta que el usuario lo apruebe. RB-1521 y RB-IA-2191 están en `datasets/en_espera/` y no se abren. El orden oficial del tablero sigue siendo D1 y después D2.

En esta etapa no hay motor general. El código de BES-jun vive dentro de su expediente y solo transcribe fórmulas de ese libro. No se entrena un modelo, no hay pronóstico y las reglas siguen candidatas.

El cierre del análisis aislado está en `datasets/en_uso/BES-jun/`. El informe es `reports/informe_analisis_BES-jun.md`, con PDF en `pdf/informes/` y los doce cuadernos en `pdf/notebooks/`. La auditoría está en `docs/revision_notebooks_auditoria.md` del expediente. Sigue **Listo para revisión**, no Completo: las consultas CT-01 a CT-08 y P-14 siguen abiertas. No se movió a `procesadas/`.

Cuando las dos condiciones de arriba estén satisfechas, se actualiza el estado de la etapa 4 y se continúa con la implementación del motor común.

Los MD5 de D1, D2, E1, X1, A1 y R1 coinciden con los de `asesor-esp/data/raw/README.md`. Hay dos copias adicionales del DOCX de ecuaciones, `(2)` y `(3)`, con el mismo MD5 que E1.

## 1. Objetivo del trabajo

Comprender cómo opera un sistema de bombeo electrosumergible (VESP/ESP), aprender sus variables y ecuaciones físicas, y construir un modelo determinístico general con reglas operacionales explícitas. El modelo tendrá un núcleo común, derivado de las ecuaciones revisadas, y un adaptador de datos para cada archivo. Se aplicará a cada Excel por separado; el primer libro, que contiene datos de varios pozos, será el primer caso de trabajo, no un modelo exclusivo para ese archivo. Las filas de libros distintos no se mezclarán.

Una vez que el mismo núcleo determinístico se haya ejecutado y evaluado, archivo por archivo, con todos los datasets entregados que tengan datos utilizables, se planificará la instalación y configuración de un modelo generativo de lenguaje (GLM, según la nomenclatura del equipo). Este recibirá un resumen estructurado de las variables de entrada y su calidad, junto con los resultados del modelo determinístico y las reglas activadas. Su función será explicar en lenguaje claro qué datos se recibieron, qué indican los cálculos y qué verificaciones o sugerencias respaldadas por reglas puede considerar el operador. No calculará PIP ni otras variables físicas por sí mismo, no inventará observaciones y no escribirá setpoints o comandos de control.

El resultado esperado es una ruta de aprendizaje y un prototipo reproducible. Este trabajo no equivale a una validación para producción ni busca recrear el algoritmo propietario SensorLess descrito en el artículo.

## 2. Alcance acordado y decisiones de partida

- El objetivo inicial es entender el sistema y aprender a usar sus variables y fórmulas físicas.
- Se construirá un solo núcleo determinístico general con las fórmulas revisadas. Los libros de Excel se conectarán al núcleo mediante adaptadores que mapeen sus columnas y unidades a un esquema de entrada común.
- El primer libro de Excel contiene datos de varios pozos y será el primer dataset aplicado al núcleo común. Cursor debe identificar cómo se distinguen los pozos antes de procesar registros.
- Cada libro Excel se perfila, limpia, adapta, procesa y reporta por separado. No se concatenan libros ni se tratan como una única serie. Los adaptadores pueden variar por archivo; las fórmulas y reglas aprobadas permanecen en el núcleo común.
- El orden de desarrollo es: fundamentos y trazabilidad de fuentes; revisión y adaptación de cada dataset; modelo determinístico general; ejecución y evaluación individual de todos los datasets; reglas; instalación y configuración posterior del GLM explicativo.
- Las recomendaciones del prototipo serán de apoyo a decisiones y requerirán revisión humana. No se implementará control automático.
- Las ecuaciones del DOCX y las fórmulas de la planilla XLSM se estudiarán y compararán. No se asumirá que son equivalentes ni se combinarán sin justificar cada diferencia.
- El artículo SensorLess y el PDF de diseño ESP se usarán como material contextual. No se copiará ni afirmará reproducir un sistema patentado.
- Los datos originales se conservan sin cambios. Las transformaciones, modelos, reportes y pruebas se guardan en rutas separadas.
- No se enviarán datos de pozos, identificadores ni documentos restringidos a agentes o modelos en la nube hasta confirmar autorización. Si no está confirmada, se trabajará con recursos locales o con datos anonimizados.

### Terminología de trabajo

- **BEP:** Best Efficiency Point o punto de mejor eficiencia. Es el caudal y la altura en que una bomba alcanza su eficiencia máxima para una velocidad y configuración de impulsor determinadas. Se identifica en la curva del fabricante; no se deben inventar límites de operación alrededor del BEP. Fuente de referencia: Hydraulic Institute, [Pump Curves](https://datatool.pumps.org/pump-fundamentals/pump-curves.html).
- **VESP / ESP / BES:** se registrará la nomenclatura que utiliza cada fuente. El glosario indicará equivalencias sin cambiar encabezados originales de los datos.
- **GLM:** nombre usado por el equipo para el modelo generativo de lenguaje que se instalará en una etapa posterior. En la etapa 7 se definirá la familia, versión y modalidad de ejecución, según privacidad, costos y requisitos de uso.
- **PIP, PWF, THP, Q, H, η, BEP:** cada sigla o símbolo nuevo se define en un glosario, con unidad, fuente, significado operacional y límites conocidos.

## 3. Registro de entradas y uso esperado

| Archivo recibido | Uso en el trabajo | Tratamiento inicial |
|---|---|---|
| RB-1521-PY-121120.xls | Primer dataset que se aplicará al modelo determinístico general; contiene datos de varios pozos según el alcance confirmado | Perfil por hoja y por pozo. Identificar llave de pozo, fecha, unidades y significado de mediciones y cálculos antes de adaptarlo al esquema común. |
| RB-IA-2191-Data.xlsx | Dataset adicional para aplicar y evaluar el mismo modelo determinístico | Analizar como dataset independiente. No unir con el primer libro ni presumir que representa el mismo pozo. |
| Copia de Copia de Ecuaciones  _.xlsm | Fuente de fórmulas y cálculos existentes, incluida la hoja Prueba Sesnorless | Inspeccionar fórmulas, hojas, celdas de entrada y salida de forma estática. No ejecutar macros VBA. |
| Modelo_Sensorless_PIP_ESP_Set_Ecuaciones.docx | Fuente técnica del modelo algebraico y del observador propuesto | Extraer ecuaciones, supuestos, parámetros requeridos, unidades y guardrails. |
| Modelo_Sensorless_PIP_ESP_Set_Ecuaciones (1).docx | Copia duplicada del DOCX anterior | Registrar como duplicado y evitar procesarlo dos veces, salvo que una versión futura tenga contenido distinto. |
| 004-ESPdesign.pdf | Material de fundamentos de diseño y selección ESP | Usar para aprender el contexto, documentando qué conceptos aplican al caso y cuáles no. |
| paper_sensorless - v2.docx | Antecedente de implementación y validación SensorLess | Usar como contexto y referencia de preguntas. Sus métricas no se atribuyen a este proyecto sin datos originales que las respalden. |

Antes de procesar, el coordinador volverá a verificar los nombres exactos y calculará un hash SHA-256 para conservar trazabilidad entre fuentes, copias y resultados.

## 4. Organización de carpetas en Cursor

Mantener una estructura equivalente a esta en el proyecto de Cursor:

| Carpeta o archivo | Contenido |
|---|---|
| trabajo.md | Plan maestro, estado, bloqueos, decisiones y evidencia de aceptación. Solo lo actualiza el coordinador. |
| fuentes/originales/ | Copias de los archivos recibidos, sin editar y con acceso de solo lectura cuando sea posible. |
| docs/ | Glosario, inventario, diccionarios de datos, decisiones, fórmulas trazadas y manual para operador. |
| data/perfiles/ | Perfiles de calidad y esquemas, uno por libro de Excel. |
| data/procesados/por_archivo/ | Copias limpias y derivadas, separadas por libro y con el archivo de origen anotado. |
| src/adaptadores/por_archivo/ | Adaptadores que mapean cada libro a un esquema de entrada común, sin duplicar ni cambiar las ecuaciones del núcleo. |
| src/modelo_deterministico/ | Funciones físicas, conversiones y resolución numérica. |
| src/reglas/ | Reglas operacionales explícitas y trazables. |
| src/asistente/ | Capa conversacional, creada después de superar la etapa determinística. |
| tests/ | Pruebas de datos, unidades, ecuaciones, reglas e interacción del asistente. |
| reports/por_archivo/ | Gráficos, métricas y resultados de cada Excel por separado. |
| logs/ | Bitácora de ejecución, resultados de agentes y comandos reproducibles. |

No se modifican ni renombran los originales. Si el repositorio de trabajo ya tiene una estructura estable, Cursor debe respetarla y mapear estas rutas a su organización existente.

## 5. Método de procesamiento de cada Excel

Para cada libro se crea un expediente independiente:

1. Registrar nombre, tamaño, hash, hojas, dimensiones, fecha de extracción y versión de herramientas.
2. Distinguir valores ingresados, fórmulas y valores calculados. No reemplazar fórmulas por sus resultados sin preservar ambas vistas.
3. Identificar pozo, fecha/hora, unidad y fuente de cada campo. Registrar por separado datos medidos, parámetros fijos, valores estimados y resultados de fórmulas.
4. Generar un diccionario con nombre original, nombre normalizado, descripción, unidad, tipo, rango observado, faltantes, regla de conversión y nivel de confianza del mapeo.
5. Revisar filas duplicadas, fechas desordenadas, faltantes, valores constantes, saltos, rangos atípicos y cambios de frecuencia. Marcar los hallazgos; no borrar ni corregir datos sin una regla documentada.
6. Guardar el resultado limpio bajo data/procesados/por_archivo/<archivo>/, junto con el adaptador, el script de transformación y un informe de cambios. Mantener una copia fiel del origen.
7. Mapear las variables disponibles al esquema de entrada común del núcleo determinístico. Registrar campos no mapeados, conversiones y requisitos faltantes; no cambiar ecuaciones para acomodar silenciosamente un archivo.
8. Ejecutar el mismo núcleo y sus pruebas con ese libro de forma aislada. El informe debe poder regenerarse sin leer los resultados de otros Excel.

Si no se puede identificar a qué pozo pertenece una fila del primer Excel, no se debe agrupar ni evaluar registros entre pozos hasta resolver esa llave. Si faltan unidades o una señal física necesaria, se registra como bloqueo de ese caso; no se infiere ni imputa silenciosamente. El núcleo puede procesar otro archivo si su adaptador y datos sí cumplen los requisitos, pero cada limitación debe quedar visible.

## 6. Etapas de trabajo

### Etapa 0 — Preparar el proyecto y proteger las fuentes

**Entradas:** archivos recibidos, alcance de este plan y workspace de Cursor.  
**Proceso:** crear la estructura, copiar fuentes sin cambios, calcular hashes, registrar versiones y confirmar si los agentes usados procesarán datos localmente o en la nube.  
**Salidas:** inventario inicial, copia de trabajo de originales, bitácora y lista de decisiones pendientes.  
**Aceptación:** se puede demostrar qué fuente produjo cada salida; los archivos originales siguen intactos; el estado de privacidad está documentado.  
**Estado:** Funcional. Evidencia: hashes SHA-256 y MD5, copias en `fuentes/originales/` con el mismo hash, bitácora en `logs/bitacora.md`. Falta revisión independiente; no está Completa.

### Etapa 1 — Aprender la operación VESP/ESP y construir el glosario

**Entradas:** PDF de diseño ESP, DOCX de ecuaciones, XLSM y artículos técnicos que se autoricen.  
**Proceso:** dibujar el recorrido del fluido y de la energía; explicar bomba, motor, variador, cable, tubing, fluido y variables de fondo y superficie. Estudiar BEP y su relación con curvas Q-H-η, punto de operación, frecuencia, caudal y altura. Separar conceptos generales de los datos específicos de cada pozo.  
**Salidas:** docs/glosario.md, docs/mapa_del_sistema.md y material pedagógico con ejemplos tomados de los anexos, identificando sus supuestos.  
**Aceptación:** otra persona puede explicar cada término y rastrearlo a una fuente; las unidades y las diferencias entre PIP, PWF y THP están claras.  
**Estado:** En curso. Se usan los conceptos de `trabajo2.md` §3 y el glosario del artículo. `docs/conceptos/esp_101.md` de asesor-esp todavía no existe.

### Etapa 2 — Inventariar y perfilar las fuentes

**Entradas:** todos los archivos originales.  
**Proceso:** registrar metadatos y duplicados; revisar las hojas de cada Excel por separado; perfilar columnas, fórmulas, fechas, pozos y calidad. En el primer Excel, localizar cómo están identificados los varios pozos. En la planilla XLSM, mapear qué celdas son entradas, intermediarios y salidas sin ejecutar VBA.  
**Salidas:** docs/inventario_fuentes.md, un diccionario por Excel, un perfil por Excel, mapa de celdas de la planilla XLSM y lista de faltantes.  
**Aceptación:** cada campo usado tiene descripción, unidad o una marca visible de “unidad pendiente”; se conoce el origen de cada resultado. Los libros no se mezclan.  
**Estado:** En curso para el catálogo común. BES-jun está perfilado dentro de `datasets/en_uso/BES-jun/`. D1 y D2 siguen en espera, sin leer sus filas.

### Etapa 3 — Trazar y reconciliar las ecuaciones

**Entradas:** DOCX de ecuaciones, fórmulas del XLSM, datos disponibles y manuales o curvas autorizados.  
**Proceso:** transcribir cada ecuación en un registro con identificador, variables, unidad esperada, fuente, supuestos, rango válido y prueba numérica. Comparar el modelo algebraico del DOCX con la cadena de pérdidas y el cálculo de PIP de la hoja Prueba Sesnorless. Explicar coincidencias, diferencias y datos requeridos. Seleccionar una formulación base solo después de esta revisión.  
**Salidas:** docs/trazabilidad_ecuaciones.md y docs/decision_modelo_base.md.  
**Aceptación:** cada fórmula implementable tiene trazabilidad, conversión de unidades verificada y un ejemplo reproducible; las diferencias no quedan ocultas bajo una única fórmula. Si faltan parámetros, la salida debe quedar bloqueada o marcada como demostración, no como estimación validada.  
**Estado:** En curso, como lectura y trazabilidad. La puerta de fórmulas no está satisfecha: el borrador está en `docs/trazabilidad_ecuaciones.md` y `docs/decision_modelo_base.md`, y G1 no está aprobada. Esa puerta es la condición 2 del bloqueo del motor.

### Etapa 4 — Construir el núcleo determinístico general

**Entradas:** ecuaciones reconciliadas, esquema de entrada común, diccionarios de los Excel y parámetros físicos disponibles.  
**Proceso:** implementar una sola colección de funciones físicas para conversiones, curvas de bomba, pérdidas, potencia, búsqueda numérica de Q cuando corresponda, PIP y validaciones físicas. Mantener el núcleo independiente del nombre y la disposición de columnas de cada libro; convertir unidades al entrar y salir mediante reglas explícitas. Mantener las reglas operacionales separadas del cálculo.  
**Salidas:** núcleo determinístico general, especificación de su interfaz, pruebas unitarias y ejemplos reproducibles con entradas del esquema común.  
**Aceptación:** para un mismo caso y parámetros, el cálculo es reproducible; pruebas de unidades y límites pasan; no se produce una estimación cuando faltan señales esenciales o la operación queda fuera del dominio de las curvas. Se puede invocar el mismo núcleo con datos de cualquier archivo que cumpla su esquema de entrada, sin copiar las fórmulas por dataset. El resultado incluye Q/PIP estimados cuando sea posible, entradas utilizadas, residuales, límites aplicados y motivos de advertencia.  
**Estado:** Bloqueada para el núcleo común. Faltan la respuesta de P-14 y la puerta de fórmulas (`docs/decisiones_pendientes.md`). La transcripción de celdas de BES-jun está en su expediente y no es el núcleo común. El núcleo de `asesor-esp` (T4.1 a T4.14) no está implementado.

### Etapa 5 — Aplicar y evaluar el modelo en todos los Excel, uno por uno

**Entradas:** núcleo determinístico aprobado, adaptadores por archivo y todos los Excel que contienen datasets utilizables.  
**Proceso:** ejecutar secuencialmente o en trabajos aislados el mismo núcleo sobre cada libro, usando su adaptador y conservando sus resultados separados. Esta etapa evalúa un modelo determinístico; no incluye entrenamiento ni mezcla de registros. Comparar con PIP medida solo cuando su origen y unidad estén confirmados; usar MAE, RMSE, sesgo y error porcentual cuando corresponda. Si no hay referencia válida, evaluar consistencia física, cobertura de variables y límites del modelo, y declarar que no se pudo medir exactitud.  
**Salidas:** un reporte, gráficos y registro de cobertura por cada Excel en reports/por_archivo/; resumen global de qué archivos fueron procesados, cuáles quedaron bloqueados y por qué, sin consolidar sus filas.  
**Aceptación:** se ha aplicado el mismo núcleo a cada dataset utilizable; ningún resultado de un archivo se presenta como validación de otro; métricas y exclusiones son reproducibles; el umbral de aceptación queda acordado antes de declarar el modelo apto. No se heredan métricas del paper SensorLess. Para avanzar al GLM, todos los archivos dataset deben tener una ejecución documentada o un bloqueo justificado y aprobado.  
**Estado:** Bloqueada para aplicar un motor común. El informe `datasets/en_uso/BES-jun/reports/analisis_preliminar.md` compara la transcripción con la caché de ese libro. No es una predicción ni una evaluación de otros Excel. D1 y D2 no se ejecutaron.

### Etapa 6 — Construir y revisar el conjunto de reglas operacionales

**Entradas:** salidas del modelo, límites de fabricante y decisiones revisadas por especialista.  
**Proceso:** documentar para cada regla su condición, rango/unidad, fuente, prioridad, explicación y acción sugerida. Incluir reglas de calidad de datos, rango de bomba, proximidad al BEP solo si hay curva válida, tendencias y señales contradictorias. Establecer qué hacer cuando falten datos: solicitar la medición, advertir y abstenerse de recomendar.  
**Salidas:** docs/catalogo_reglas.md y suite de escenarios de prueba.  
**Aceptación:** cada sugerencia se puede rastrear a una regla revisada; no hay umbrales inventados ni recomendaciones que dependan de una variable desconocida.  
**Estado:** Bloqueada para aprobación. Las candidatas de `docs/reglas_candidatas.md` siguen pendientes de revisión. Ninguna está aprobada.

### Etapa 7 — Instalar y configurar el GLM para explicar los datos

**Entradas:** núcleo determinístico aplicado y evaluado con cada dataset utilizable, adaptadores, catálogo de reglas, glosario y documentación autorizada.  
**Proceso:** primero decidir dónde se ejecutará el GLM (local o servicio autorizado) según privacidad, recursos y costos; luego instalar/configurar la familia y versión elegidas. Definir el contrato de entrada para cada pozo y periodo: variables recibidas con unidad, estado de calidad/faltantes, resultados determinísticos, reglas activadas y referencias a fórmulas o fuentes. El GLM convertirá ese contexto a una explicación natural para el operador: qué datos llegaron, qué muestran los cálculos, qué evidencia lo respalda, qué incertidumbre existe y qué verificaciones o sugerencias basadas en reglas puede considerar. Mantener los cálculos y la activación de reglas fuera del GLM; no enviar libros completos sin selección y control de datos.  
**Salidas:** GLM instalado/configurado en el entorno aprobado, interfaz estructurada de entrada/salida, prototipo conversacional acotado, instrucciones de sistema, escenarios de prueba y manual de uso.  
**Aceptación:** en escenarios de prueba el asistente explica fielmente las observaciones recibidas y los resultados calculados, conserva unidades, cita las reglas o fuentes que sustentan sus sugerencias, no inventa valores ni causas, reconoce datos faltantes y no altera el cálculo. Toda sugerencia requiere criterio del operador; no existen escrituras a PLC/VFD ni cambios de setpoint. La conexión a nube permanece bloqueada hasta contar con autorización documentada.  
**Estado:** Pendiente.

### Etapa 8 — Integrar, revisar y entregar

**Entradas:** código, reportes, glosario, pruebas y resultados de todas las etapas anteriores.  
**Proceso:** revisión independiente de ecuaciones, datos, código y textos del asistente; ejecutar la suite completa desde una instalación limpia; registrar comandos y versiones; resolver defectos críticos; actualizar bitácora y este plan.  
**Salidas:** repositorio reproducible, informes por archivo, manual del operador, decisiones, bitácora y versión final de trabajo.md.  
**Aceptación:** una persona que no desarrolló el código puede reproducir el perfil, el cálculo, las pruebas y un diálogo del prototipo siguiendo las instrucciones.  
**Estado:** Pendiente.

## 7. Coordinación multiagente en Cursor

### Roles

- **Coordinador:** conserva el alcance, asigna tareas, resuelve dependencias, revisa las evidencias y es el único que modifica trabajo.md.
- **Agente de dominio y fuentes:** prepara glosario, mapa VESP/ESP, inventario de ecuaciones y trazabilidad técnica.
- **Agentes de datos:** perfilan un Excel cada uno, de forma aislada, con informe y diccionario propios. No cambian los archivos originales ni procesan otros libros.
- **Agente de modelo:** implementa el núcleo determinístico común, sin lógica específica de un dataset, solo después de aprobar docs/decision_modelo_base.md y el esquema de entrada.
- **Agente de QA:** revisa el cálculo y ejecuta pruebas independientes; no aprueba su propio trabajo.
- **Agente GLM:** instala y construye la capa de lenguaje solo después de superar las etapas 4, 5 y 6 y revisar el permiso de ejecución en el entorno seleccionado.

### Reglas de ejecución

1. Dividir cada encargo en una tarjeta con ID, objetivo, entradas, archivos que puede leer/escribir, dependencias, salida esperada, criterios de aceptación y pruebas.
2. Paralelizar únicamente tareas independientes. Se pueden perfilar libros distintos en paralelo, pero cada informe debe quedar separado. No instalar ni ejecutar el GLM antes de validar cálculo y reglas.
3. No permitir que dos agentes editen el mismo archivo al mismo tiempo. Las fuentes originales son de solo lectura.
4. El agente devuelve archivos cambiados, pruebas ejecutadas, resultados, dudas y bloqueos. El coordinador revisa y registra evidencia en trabajo.md.
5. Una tarea pasa a “Revisada” cuando otro agente revisó el resultado. Pasa a “Funcional” cuando las pruebas especificadas se ejecutaron y sus resultados quedaron guardados. Solo se marca “Completa” cuando cumple ambas condiciones.
6. Si una tarea no tiene datos, unidades, permisos o parámetros suficientes, se marca “Bloqueada” con la pregunta concreta necesaria. No se rellena con valores ficticios.

### Estados y evidencia

| Estado | Significado |
|---|---|
| Pendiente | No se ha iniciado. |
| En curso | Un agente tiene la tarjeta asignada. |
| Bloqueada | Falta una decisión, dato, unidad o permiso. |
| Revisada | Un revisor distinto del autor comprobó el resultado. |
| Funcional | Pasó las pruebas definidas y la evidencia está guardada. |
| Completa | Está revisada y funcional; se registra evidencia verificable. |

Cada tarjeta completada debe registrar en la bitácora: fecha, agente autor, revisor, fuentes utilizadas, cambios, pruebas, ruta de evidencia, limitaciones y próxima dependencia.

## 8. Prompt maestro para Cursor

Usa este prompt al abrir el proyecto en Cursor:

> Lee trabajo.md completo y úsalo como plan de control del proyecto. Antes de programar, verifica la estructura y las fuentes sin modificarlas. Ejecuta solo etapas cuyas dependencias estén satisfechas. Construye un único núcleo determinístico general a partir de las ecuaciones aprobadas y procesa cada libro por separado mediante su adaptador al esquema común; conserva los datos originales y nunca mezcles filas de libros distintos. No inventes unidades, límites de operación ni valores faltantes; registra toda incertidumbre como bloqueo o advertencia. No ejecutes macros del XLSM. No envíes datos de pozos a servicios de IA en la nube sin autorización documentada. Instala/configura el GLM solo después de que el núcleo se haya aplicado y evaluado en todos los datasets utilizables y las reglas estén revisadas. El GLM recibirá variables de entrada con unidades y calidad, resultados determinísticos y reglas activadas; los explicará en lenguaje natural para un operador, sin recalcular ni inventar. Ninguna recomendación debe cambiar un setpoint. Al terminar cada tarjeta, entrega cambios, pruebas, evidencia y bloqueos al coordinador. Solo el coordinador actualiza el estado de trabajo.md y marca una tarea completa cuando está revisada y funcional.

### Primer encargo en Cursor

> Ejecuta únicamente las etapas 0, 1 y 2. No programes el modelo ni combines libros. Produce inventario de fuentes, glosario inicial, mapa del sistema, perfiles independientes de cada Excel y un mapa de entradas, fórmulas y salidas del XLSM sin ejecutar macros. En el primer Excel, identifica la llave que distingue los pozos y anota cualquier ambigüedad. Cierra con una lista priorizada de datos y decisiones que bloquean la etapa 3. Entrega evidencia reproducible y espera revisión del coordinador.

### Secuencia de encargos para Cursor

| Orden | Etapas | Encargo y condición para avanzar |
|---|---|---|
| 1 | 0–2 | Inventariar fuentes, aprender el sistema y perfilar cada archivo por separado. Avanzar cuando los perfiles, unidades conocidas y faltantes estén revisados. |
| 2 | 3 | Trazar y reconciliar ecuaciones; definir formulación física aprobada y esquema de entrada común. No programar el motor hasta cerrar esta puerta y P-14. |
| 3 | 4 | Implementar y probar el núcleo determinístico general, independiente de columnas y nombres de archivos. Solo después de la respuesta documentada de P-14 y de la puerta de fórmulas. Avanzar cuando pruebas de unidades, fórmulas y límites pasen. |
| 4 | 5 | Crear/revisar un adaptador por Excel y ejecutar el mismo núcleo sobre cada dataset de manera aislada. Avanzar cuando cada archivo tenga reporte funcional o bloqueo documentado. |
| 5 | 6 | Revisar y probar reglas operacionales con fuentes y responsables técnicos identificados. |
| 6 | 7 | Seleccionar e instalar/configurar el GLM en el entorno autorizado; probar que convierte entradas y resultados estructurados en explicaciones naturales fieles y trazables. |
| 7 | 8 | Revisión final independiente, reproducción desde instalación limpia y cierre de evidencias. |

## 9. Lista inicial de pendientes

Las marcas de completado reflejan acuerdos y revisión preliminar realizados antes de iniciar el desarrollo en Cursor. No equivalen a validar el modelo.

- [x] Acordar la meta educativa y el orden: modelo determinístico primero, explicador generativo después.
- [x] Acordar un núcleo determinístico general, aplicado a cada Excel por separado mediante adaptadores; el primer Excel es el primer caso de trabajo.
- [x] Acordar que el GLM se instalará después de evaluar el núcleo en todos los datasets utilizables y explicará las variables recibidas y sus resultados para revisión humana, sin control automático.
- [x] Revisar preliminarmente nombres, tipos y estructura de los anexos.
- [ ] Confirmar en el proyecto de Cursor el permiso para usar datos identificables con agentes/modelos alojados en la nube.
- [x] Registrar que el archivo leído en esta iteración es `Copia de FINAL BES-jun.xlsx`, distinto de D1 y D2, sin incorporarlo al tablero de asesor-esp.
- [ ] Cerrar P-14 en `docs/decisiones_pendientes.md` con respuesta, fecha, responsable y efecto en el orden de procesamiento. Hoy la respuesta está vacía.
- [ ] Localizar y documentar el identificador de pozo y las unidades del primer Excel del plan v1.0 (D1). En BES-jun hay dos códigos por hoja (Cluster y Pozo) y el libro no declara la llave; varias unidades siguen pendientes.
- [ ] Confirmar qué columnas son referencias medidas y cuáles son valores calculados o parámetros.
- [ ] Comparar las ecuaciones del DOCX y de la planilla XLSM y aprobar la formulación base.
- [ ] Confirmar parámetros y curvas de bomba requeridos para los pozos que se puedan modelar.
- [ ] Acordar el umbral cuantitativo de aceptación del cálculo antes de declarar validación.

## 10. Condiciones para declarar el prototipo listo

El prototipo puede declararse listo para demostración cuando:

1. El modelo determinístico y sus unidades están trazados y probados.
2. El mismo núcleo se ha ejecutado sobre cada dataset utilizable, con resultados informados de forma independiente; cualquier archivo no procesable tiene un bloqueo documentado.
3. La precisión se compara contra una referencia identificada o se declara expresamente que no existe referencia suficiente.
4. Las reglas operacionales tienen fuente, límite válido y aprobación técnica.
5. El asistente usa resultados estructurados, muestra el fundamento de sus respuestas y reconoce incertidumbre.
6. Una persona operadora puede entender qué muestra el sistema y qué debe verificar.
7. No hay acciones automáticas sobre equipos ni recomendaciones fuera de las reglas aprobadas.
8. Las pruebas, reportes, versiones y decisiones se pueden reproducir desde el repositorio.

