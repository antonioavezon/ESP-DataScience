# Desarrollo de la plataforma web HUC

Fecha de esta versión: 2026-10-21. Entorno en el que se construyó y se ejecutó: Fedora 43, Python 3.14.8 en `/home/antonio/projects/HUC/.venv`.

## A. Objetivo general

HUC estudia pozos con bombeo electrosumergible a partir de expedientes separados. El trabajo científico ya hecho —lectura del libro, modelos de transcripción, reglas candidatas y contratos— vive en cada expediente. No había una aplicación que un operador pudiera abrir en el navegador para ver ese material sin entrar a los cuadernos.

Esta plataforma es esa capa. Muestra qué expedientes existen, en qué etapa del ciclo están, qué pozos y resultados ya fueron calculados, y permite repetir una evaluación determinística llamando al motor que ya pasó las pruebas. El asistente local, vía Ollama, solo explica el contexto que la propia aplicación le entrega. No calcula otra física y no autoriza cambios de operación.

La relación con el proyecto científico es de lectura. La web no reescribe fórmulas, no guarda otra copia del Excel y no presenta una regla `pendiente_validacion` como si estuviera aprobada.

## B. Estado inicial

Antes de esta carpeta no había un proyecto Django. `docs/estado_proyecto.md` listaba la aplicación gráfica y la integración con un modelo de lenguaje como trabajo no empezado. `asesor-esp/` es un esqueleto de otro motor, en unidades SI, y no consume el paquete de BES-jun.

Lo que se reutiliza:

- El ciclo de carpetas `datasets/en_espera`, `en_uso` y `procesadas`.
- `dataset.md` de BES-jun, RB-1521 y RB-IA-2191.
- El paquete `datasets/en_uso/BES-jun/integracion/` (manifiesto 0.4.2, contrato 1.3.0, catálogo de reglas 1.1.0, pozos, variables, reglas y esquemas).
- `data_procesados/resultados_deterministicos.csv`, con las columnas reales del archivo, no con un esquema supuesto.
- `evaluacion.motor.evaluar_solicitud`, que valida la entrada y llama a los tres modelos de transcripción.
- `integracion/capa_linguistica.md` y `docs/discrepancias_cientificas.md` como texto de contexto, citando la ruta.
- El servicio Ollama que ya estaba en `127.0.0.1:11434`, con el modelo `qwen3:4b-instruct-2507-q4_K_M` instalado.

La raíz de HUC no es un repositorio Git. No había commits que preservar ni que revertir. No se tocó el `requirements.txt` científico de la raíz.

La línea base, tomada antes de escribir la aplicación, fue de 182 pruebas aprobadas del expediente en 20,42 s.

## C. Arquitectura

`web/config` es el proyecto Django 6.0.9. Las aplicaciones son `core`, `datasets`, `evaluaciones` y `asistente_ia`. No hay panel de administración ni usuarios: es una herramienta local de desarrollo.

Los servicios no son aplicaciones de Django. `dataset_registry` descubre fichas. `huc_adapter` es el único lugar que decide si un identificador tiene motor. Hoy esa decisión es «BES-jun, y solo si existen `motor.py` y los dos esquemas». Cualquier otro expediente usa el adaptador que responde `no_disponible` y explica la causa. Las plantillas preguntan `puede_evaluar` y no comparan el nombre.

El flujo de datos de una evaluación es: formulario, validación de pozo y de números, solicitud JSON, `evaluar_solicitud`, recorte del resultado a la sesión, plantilla. El flujo del asistente es: contexto con fuentes, comprobación de que el modelo está instalado, `POST /api/chat`, descarte de `thinking`, plantilla.

Ollama no es una dependencia de arranque. Si el puerto no responde, el dashboard lo dice y el resto de las páginas sigue cargando.

La base SQLite de `web/db.sqlite3` solo almacena la sesión (dataset elegido, modelo, límites y la última respuesta). No hay tablas de pozos.

El detalle está en `docs/02_arquitectura_web.md`.

## D. Funcionalidades implementadas

**Dashboard.** Lee el registro y el estado de Ollama. Muestra el modelo configurado, el dataset de la sesión (o el primero en `en_uso`), cuántos expedientes hay, cuántos pozos hay en fichas `pozos.json` y cuántas filas hay en CSV existentes. Si no hubiera fichas de pozos, el recuadro diría «No disponible» en lugar de un cero inventado. Las limitaciones salen del manifiesto. Para BES-jun son cuatro: identidad sin confirmar, ninguna regla aprobada, CT-01 a CT-10 abiertas y el rango de frecuencia observado que no es un límite autorizado.

**Datasets.** Tabla con ciclo, estado declarado en `dataset.md`, presencia de entrada, de resultados y de contratos, y la fecha de modificación de la ficha en UTC. El detalle de BES-jun lista los cinco pozos (QF-084, QF-301, QF-147, QF-005, QF-306), las variables con su unidad y el CSV. `pip_ft` lleva la nota de CT-03 porque el archivo de discrepancias la menciona. RB-1521 y RB-IA-2191 muestran la causa de espera y «No disponible» donde no hay paquete. No hay acción de promover una carpeta.

**Pozo.** La ficha de integración (hoja, identidad provisional, bomba, profundidades) y la fila del CSV. Un campo vacío se vería como «No disponible». Un cero real, si existiera en el archivo, se mostraría como cero.

**Evaluaciones.** Si el dataset seleccionado no puede evaluarse, el formulario no se ofrece y se lee la causa. Si puede, se elige un pozo de su `pozos.json` y, en blanco, las siete mediciones operacionales del contrato, cada una con su unidad. En blanco significa «usar la hoja». El texto «alto» en la frecuencia responde 400 y no llama al motor. La ejecución real de QF-084 sin mediciones devolvió `completada_preliminar`, activó RC-BES-03 y dejó la recomendación operacional en falso. El estado de la regla sigue en `pendiente_validacion`.

**Asistente.** Caja de consulta, pozo opcional para adjuntar la fila del CSV, respuesta, duración, tokens, `done_reason` y la lista de fuentes. Un `done_reason` de `length` se anuncia como respuesta incompleta.

**Configuración de IA.** Lista los modelos de `/api/tags`, permite elegir uno que exista, fija el tope de tokens (32 a 1024) y el tiempo (5 a 120 s), prueba la conexión y lanza una pregunta fija sobre PIP. En esta máquina el servicio listó seis modelos. `qwen3:4b` aparece con el aviso de razonamiento. Elegir un nombre que no está instalado no reemplaza la selección anterior.

**Acerca.** Explica la frontera con el expediente y con `asesor-esp`, y que no hay inicio de sesión.

## E. Instrucciones de instalación

Estas órdenes son para Fedora 43, con el entorno virtual que ya existe en el repositorio. No usan `dnf` porque el intérprete y las bibliotecas científicas ya están en `.venv`. No hace falta un segundo entorno.

1. Situarse en la carpeta de la aplicación. Así `manage.py` encuentra `config.settings`.

```bash
cd /home/antonio/projects/HUC/web
```

2. Instalar Django y httpx dentro del entorno del repositorio. `pip` de ese intérprete no toca los paquetes del sistema Fedora. Las versiones quedan fijadas en `web/requirements.txt` (Django 6.0.9, httpx 0.28.1). En la máquina de desarrollo ya se ejecutó y ambos quedaron instalados.

```bash
/home/antonio/projects/HUC/.venv/bin/python -m pip install -r requirements.txt
```

3. Opcional: exportar las variables. Si no se exportan, la aplicación usa los defaults de desarrollo (depuración activa, hosts `127.0.0.1` y `localhost`, Ollama local y el modelo Instruct). Un archivo `.env` no se carga solo; hay que exportar las variables en la shell o en el servicio que arranque Django. La plantilla está en `.env.example`. No se creó un `.env` con una clave real.

```bash
export DJANGO_SECRET_KEY="$(/home/antonio/projects/HUC/.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export DJANGO_DEBUG=1
export DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
export OLLAMA_BASE_URL=http://127.0.0.1:11434
export OLLAMA_MODEL=qwen3:4b-instruct-2507-q4_K_M
export OLLAMA_TIMEOUT_S=60
export OLLAMA_NUM_PREDICT=512
```

`DJANGO_SECRET_KEY` firma la cookie de sesión. La orden de Python genera una clave aleatoria en esta shell; no queda escrita en el repositorio.

4. Crear las tablas de sesión. En esta versión la única migración aplicada fue `sessions.0001_initial`. No crea tablas de pozos ni borra datos científicos. SQLite aparece en `web/db.sqlite3`.

```bash
/home/antonio/projects/HUC/.venv/bin/python manage.py migrate
```

5. Comprobar la configuración de Django.

```bash
/home/antonio/projects/HUC/.venv/bin/python manage.py check
```

6. Arrancar el servidor de desarrollo atado a la interfaz local. `runserver` sin dirección puede quedar más abierto; por eso se escribe `127.0.0.1:8000`.

```bash
/home/antonio/projects/HUC/.venv/bin/python manage.py runserver 127.0.0.1:8000
```

7. Abrir en el navegador `http://127.0.0.1:8000/`.

Para repetir la suite de la web:

```bash
/home/antonio/projects/HUC/.venv/bin/python manage.py test tests.test_huc_web
```

## F. Integración con Ollama

El modelo inicial es `qwen3:4b-instruct-2507-q4_K_M`. El endpoint de inferencia es `POST {OLLAMA_BASE_URL}/api/chat`. El de inventario es `GET {OLLAMA_BASE_URL}/api/tags`.

El contexto lo construye `technical_context.py`. Lleva la definición verificada de PIP, extractos acotados de la capa lingüística, de las discrepancias y del manifiesto, las limitaciones y, si hay pozo, la fila determinística. Cada bloque tiene tipo y fuente. El operador ve esa lista debajo de la respuesta.

Los errores de conexión, el tiempo agotado, el JSON inválido, el modelo ausente y la respuesta vacía se muestran como texto de error y no tumban el proceso. `done_reason=length` se rotula como incompleta. La duración y `eval_count` se guardan cuando Ollama los envía.

Límites conocidos: no hay reintento automático, no se transmite el historial de varias vueltas, el extracto de cada documento se corta a 2500 caracteres y no hay recuperación semántica. El detalle está en `docs/03_integracion_ollama.md`.

## G. Integración con el motor determinístico

Se llama a `evaluar_solicitud` en `datasets/en_uso/BES-jun/src/evaluacion/motor.py`. Esa función ya valida el contrato 1.3.0, aísla la simulación y convierte una excepción no prevista en `error_interno` con `incidente_id`. La web no envuelve las ecuaciones en otro `try` que devuelva éxito vacío.

No se invocan desde la interfaz la simulación (`modo=simulacion`), la sustitución de parámetros protegidos ni la curva de escenario. Esas vías siguen existiendo en el motor para las pruebas del expediente.

Sigue pendiente, para la web, ofrecer una simulación hipotética bien separada del modo operacional, mostrar el `incidente_id` con un enlace al registro `logs/incidentes.jsonl` sin filtrar trazas, y evaluar otros datasets cuando tengan motor propio.

## H. Casos futuros

RB-1521 y RB-IA-2191 ya aparecen porque tienen `dataset.md` en `en_espera`. Incorporarlos de verdad exige, fuera de esta aplicación, la decisión de pasarlos a `en_uso`, una copia de trabajo y un paquete de integración. Hasta entonces la web no abre el `.xls` ni el `.xlsx`.

Un dataset futuro se incorpora igual: carpeta en una de las tres etapas, `dataset.md`, y más adelante manifiesto, contratos y un adaptador en `adaptador_para`. Las vistas de lista, detalle y dashboard no necesitan un `if` nuevo si el adaptador declara pozos, resultados, limitaciones y `puede_evaluar`.

`asesor-esp` queda fuera hasta que exista un motor SI con su propio adaptador. No se copian las fórmulas de la hoja.

## I. Trabajo pendiente

| Identificador | Funcionalidad pendiente | Descripción técnica | Dependencias | Prioridad | Estado | Criterio de aceptación |
|---|---|---|---|---|---|---|
| WEB-01 | Simulación hipotética | Formulario de `modo=simulacion` que llame a `evaluar_solicitud` con escenario y parámetros permitidos, marcado como hipotético | Contrato 1.3.0 ya lo permite; falta la vista | Media | No empezado | El resultado dice `hipotetico` verdadero y no escribe la hoja |
| WEB-02 | Lectura de incidentes | Mostrar `incidente_id` y el mensaje público, sin traceback ni ruta | `logs/incidentes.jsonl` del expediente | Baja | No empezado | Un error interno de prueba se ve en la página y el archivo de log no se trunca |
| WEB-03 | RB-1521 | Adaptador cuando el expediente se procese | Decisión de promoverlo; P-14 sigue abierta | Alta cuando se autorice el expediente | Bloqueado | Hay `integracion/` real y la web no inventa pozos antes de eso |
| WEB-04 | RB-IA-2191 | Igual que WEB-03, después de D1 | El libro no se abre en esta etapa | Alta cuando se autorice | Bloqueado | Igual que WEB-03 |
| WEB-05 | Historial de consultas | Varios turnos sin mezclar el texto del operador con el sistema | Límite de tamaño de la sesión | Baja | No empezado | El segundo turno conserva las fuentes y sigue sin mostrar `thinking` |
| WEB-06 | Recuperación documental | Sustituir el recorte fijo por un recuperador, detrás de la misma estructura de bloques | Diseño; no hace falta una base vectorial para la interfaz actual | Baja | Previsto en la interfaz de contexto | Un bloque nuevo cita su archivo y las vistas no cambian |
| WEB-07 | Gráficas | Curvas solo con series ya verificadas | Decisión de qué serie y de no tratar la EFF como BEP | Baja | No empezado | La figura sale de columnas existentes y declara la unidad |
| WEB-08 | Cierre científico del PIP | No es trabajo de la web | Confirmación de la presión en el sensor | Alta para el expediente | Abierto (CT-03) | La celda se conserva hasta esa confirmación; la web solo la rotula |

## J. Riesgos y limitaciones

La reproducción de la caché de Excel no es validación experimental. El censo del expediente dejó cero fórmulas con validación externa suficiente. La interfaz lo dice en el detalle de resultados y no cambia los números.

El PIP es el riesgo que hay que seguir viendo. En las cinco hojas el sensor está más profundo que la admisión. La celda hace `P/G + TVD_sensor - TVD_intake`. La convención hidrostática alternativa, que no está en el motor, restaría esa diferencia. Para QF-554H / QF-084 la diferencia es 51,291 ft (la celda da 1714,496 ft). La procedencia del sensor no está confirmada, así que el signo no se invirtió. La web muestra el valor de la celda y la nota de CT-03. El gradiente sigue rotulado en la hoja como `psi*ft` aunque la cuenta es de psi/ft; la nota lo indica y no convierte.

Otras limitaciones que la pantalla repite desde el manifiesto o desde las discrepancias: identidad Cluster/Pozo provisional, reglas no aprobadas, BS&W rotulado en porcentaje y usado como fracción, exponente de Hazen-Williams de la hoja distinto del PDF, y frecuencia observada que no es un límite de operación.

La versión no tiene autenticación. Quien pueda abrir `127.0.0.1:8000` en esta máquina puede lanzar una evaluación de lectura y una consulta a Ollama. Por eso el servidor no debe publicarse. No hay un endpoint que ejecute órdenes del sistema ni que reciba una ruta de archivo.

## K. Pruebas realizadas

Todas el 2026-10-21, en esta máquina.

| Orden | Resultado |
|---|---|
| `pytest -q` del expediente BES-jun, antes | 182 aprobadas, 20,42 s |
| `manage.py check` | Sin problemas |
| `manage.py migrate` | Aplicó `sessions.0001_initial` |
| `manage.py test tests.test_huc_web` | 16 aprobadas, 1,600 s en la última corrida |
| `pytest -q` del expediente, después | 182 aprobadas, 20,08 s |
| curl de las diez rutas principales | 200 |
| curl de `/datasets/no-existe/` | 404 |
| POST de evaluación de QF-084 sin mediciones | `completada_preliminar`, RC-BES-03, `pendiente_validacion` |
| POST al asistente con la pregunta de PIP | Texto visible: «PIP es la presión del fluido en la entrada de la bomba electrosumergible.» Finalizada. Unos 8,8 s. |
| SHA-256 del Excel de trabajo y del original en `fuentes/originales` | `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85` en ambos, después de la evaluación |
| Navegador automatizado, 1280 px y 390 px | Menú lateral en escritorio, columna única en ancho estrecho, sin desborde horizontal. CSS 200. Sin 500 en el registro de `runserver` |

No hubo fallos en esas corridas. La suite de Django no incluye la llamada real a Ollama; esa llamada se hizo aparte, con el servicio encendido, y el resultado de arriba es el que devolvió.

El registro de `runserver` no mostró excepciones. Sí mostró el 404 esperado del identificador inexistente.

## Segunda etapa — Consola operacional interactiva ESP

### 1. Objetivo de la modificación

La primera pantalla quedó como un tablero del proyecto: conexión con Ollama, nombre del modelo, dataset seleccionado y conteos de expedientes. Un operador de bomba no necesita eso para saber cómo está el equipo ni qué cambia si mueve un parámetro. Esta etapa convierte `/` en una consola con pantalla y mandos. El registro, los datasets, las evaluaciones en formulario, el asistente y la configuración del modelo siguen existiendo, en `/administracion/` y en sus rutas anteriores.

### 2. Problemas de la interfaz anterior

La luz verde de la barra decía «Ollama responde» y el modelo activo. Eso no es el estado de la bomba. El dashboard no tenía selector de pozo, no cargaba el punto escrito en la hoja y no permitía un escenario hipotético. Mezclaba infraestructura con operación.

### 3. Arquitectura implementada

| Pieza | Archivo | Función |
|---|---|---|
| Mandos | `services/controles_fisicos.py` | Declara frecuencia, TVD de admisión, potencia y head, y deja una reserva de variables sin dibujar. |
| Escenario | `services/escenario_inicial.py` | Lee `integracion/pozos.json`. No inventa el valor que falta. |
| Motor | `services/huc_adapter.py` | `evaluar_escenario` arma la solicitud y llama a `evaluar_solicitud`. |
| Estado | `services/estado_operacional.py` | Traduce la salida del motor a los cinco rótulos. |
| Texto | `services/mensajes_operador.py` | Mensaje y acción determinísticos. Ollama solo puede reformular si no contradice el rótulo. |
| Orquestación | `services/consola_operacional.py` | No escribe el Excel. |
| API | `apps/core/api_consola.py` | Pozos, escenario y evaluación, con `evaluacion_id`. |
| Pantalla | `templates/core/consola.html`, `static/js/consola.js`, estilos en `app.css` | Selector, pantalla y mandos. |

La página administrativa sigue en `templates/core/administracion.html`.

### 4. Variables disponibles

En los cinco pozos de BES-jun la ficha trae frecuencia (Hz), TVD de admisión, de sensor y de descarga (ft), caudal registrado (BFPD), presión de sensor y THP (psi), y la curva de 60 Hz con `head_ft` y `brake_hp` por punto. El motor, al evaluar, devuelve gradiente, PIP en ft, THD total en ft y caudal de intersección en BFPD.

### 5. Origen de los valores iniciales

Salen de `condiciones_registradas` y `profundidades_ft` de `integracion/pozos.json`, no de la última fila de un archivo de series. `fecha_medicion` es null. En QF-084 `fecha_es_today` es verdadero: la fecha de la hoja es `=TODAY()` y no es una medición de este instante. La leyenda fija es: «Escenario inicial basado en datos disponibles — no corresponde a telemetría en tiempo real.»

Frecuencias registradas, distintas por pozo: QF-084 63 Hz, QF-301 57 Hz, QF-147 56 Hz, QF-005 67 Hz, QF-306 62 Hz. La TVD de admisión de QF-084 es 2653,177 ft. No se usa un solo juego de límites para todos.

### 6. Reglas de evaluación

Se reutilizan RC-BES-01, 02 y 03. Comparan el caudal registrado con los límites escritos en la misma hoja, escalados con la frecuencia. Ninguna está `aprobada_para_uso_operacional`. RC-BES-04 sigue no evaluable. El motor deja `recomendacion_operacional_autorizada` en falso. Fuera del dominio de frecuencia observado (el mínimo y el máximo de las cinco hojas) el motor advierte y calcula; ese intervalo no es un límite autorizado.

### 7. Estados operacionales

Los rótulos CORRECTO, ADVERTENCIA, PELIGRO, NO EVALUABLE y ERROR DE EVALUACIÓN correspondieron a la primera versión de la consola. La correspondencia vigente está en «Corrección UX/UI — Consola compacta tipo calculadora». RC-BES-03 sola ya no pinta un color operacional.

### 8. Integración del motor determinístico

Sin cambios respecto del valor registrado, la solicitud va en modo operacional y sin variables: el motor lee la hoja. Si la frecuencia cambia, viaja como variable operacional con unidad Hz. Si cambia la TVD de admisión, viaja en `parametros_escenario` como `{valor, unidad: ft}` y la solicitud pasa a `modo=simulacion` con `escenario_id`. El motor marca `hipotetico`, no escribe la ficha y no autoriza una recomendación. La potencia y el head se rechazan con HTTP 400 si alguien los envía como mando.

### 9. Integración de Ollama

El navegador pide primero el cálculo sin modelo y pinta el estado. Después pide la explicación, con el mismo `evaluacion_id`. El rótulo no se toma del texto del modelo. Si la respuesta viene vacía, incompleta (`done_reason=length`), contradice el estado (por ejemplo dice que la bomba está segura cuando el rótulo no es CORRECTO) o el servicio no responde, queda el mensaje determinístico. El modelo inicial sigue siendo `qwen3:4b-instruct-2507-q4_K_M`, solo en el servidor. La consola no muestra su nombre, ni tokens, ni el prompt.

### 10. Comportamiento de los potenciometros

Frecuencia y TVD de admisión tienen deslizador, número y botón Inicio. El deslizador de frecuencia va del 50 % al 150 % del valor de esa hoja. El de TVD va ±100 ft alrededor del valor registrado. Esos extremos son el recorrido del mando, con `es_limite_operacional` en falso, y la leyenda lo dice. Un número escrito fuera de ese recorrido se envía igual si es finito; la frecuencia no positiva se rechaza porque el contrato exige que sea positiva, no porque exista un límite de variador. El arrastre espera 300 ms. Cada pedido lleva un `evaluacion_id` creciente. El cliente aborta la petición anterior y descarta una respuesta cuyo id no es el vigente. Mientras tanto la pantalla dice «Evaluando escenario...» y no conserva el color anterior.

### 11. Manejo de escenarios

El escenario inicial no modifica nada. Cualquier diferencia entra como simulación. La consola lo dice en la línea «Simulación: los cambios no se aplican al pozo real.» «Restaurar valores» vuelve a los números de la ficha y a una evaluación sin sustituciones. «Inicio», en cada mando, restaura solo ese parámetro. Nada de esto se guarda en el Excel ni en `pozos.json`.

### 12. Limitaciones científicas

El PIP que se muestra es el de la celda, en ft, con la nota de CT-03. Cambiar la TVD de admisión cambia ese número porque la celda depende de la distancia al sensor; no cierra la duda del signo ni convierte ft en psi. El sensor y la descarga se ven como referencia y no se mueven. La potencia no tiene un valor de operación. El THD es salida del balance, no un head de consigna. Las reglas no autorizan a operar ni a subir o bajar la frecuencia en el pozo real. No hay telemetría en vivo.

### 13. Pruebas ejecutadas

El 2026-10-21, antes de esta etapa, el expediente BES-jun tenía 182 pruebas aprobadas en 20,14 s. Después de la consola, `manage.py test tests.test_huc_web tests.test_consola` aprobó 28 pruebas en 7,313 s. Incluyen pozos reales, frecuencias distintas, escenario inicial de QF-084 en ADVERTENCIA con RC-BES-03, paso a RC-BES-01 a 60 Hz, cambio de TVD con PIP distinto, rechazo de potencia, head, unidad psi y frecuencia cero, pozo desconocido, restauración, PELIGRO y CORRECTO solo con diccionarios sintéticos, Ollama contradictorio, caído e incompleto, y el descarte de respuestas viejas en el JavaScript. El SHA-256 del Excel de trabajo y del original sigue en `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`. En el navegador, a 1280 px, QF-084 cargó en ADVERTENCIA con PIP 1714,496 ft y THD 2083,217 ft, sin nombrar el modelo. Al pasar la frecuencia a 60 Hz la chapa cambió a modo simulación y el texto pasó a decir que el caudal supera el límite escrito, sin tratarlo como límite de seguridad. Una explicación del modelo que invertía RC-BES-03 se descartó y quedó el texto determinístico.

### 14. Funcionalidades pendientes

Caudal, presión de sensor, THP, temperatura, API y BS&W están en la reserva del registro de mandos y no se dibujan. No hay corriente de motor ni velocidad distintas de la frecuencia. No hay límite de variador en el expediente, así que no hay un tope de frecuencia que la consola pueda hacer cumplir. NORMAL y CRÍTICO no ocurren con los datos actuales. No hay adquisición en vivo.

### 15. Plan de incorporación de nuevos datasets

Un expediente entra a la consola cuando su `integracion/pozos.json` trae `pozo_rotulo` y, para evaluar, cuando el adaptador implementa `evaluar_escenario`. RB-1521 y RB-IA-2191 no tienen esa ficha: no aparecen en el selector y no se les inventan pozos. El registro administrativo sigue mostrándolos como pendientes.

## Corrección UX/UI — Consola compacta tipo calculadora

### Problemas encontrados

La consola ocupaba la pantalla como un tablero administrativo: tarjetas altas, márgenes amplios y un deslizador por fila. El encabezado decía «Modo simulación» y el pie repetía «Evaluar escenario» y «Restaurar valores iniciales», además de «Restaurar este mando» en cada control. El número visible arrastraba toda la precisión interna (por ejemplo la TVD de admisión de QF-084). Los rótulos ADVERTENCIA, CORRECTO y PELIGRO mezclaban una regla de coherencia no aprobada, una conformidad que el motor no autoriza y un límite crítico que el expediente no marca.

### Cambios realizados

Se modificó la misma aplicación en `web/`. No se creó otra. No se tocaron las fórmulas, el Excel ni los contratos de BES-jun.

La plantilla `templates/core/consola.html` deja el selector, el botón «Restaurar valores» y el aviso fijo «Simulación: los cambios no se aplican al pozo real.» La rejilla de mandos la llena `static/js/consola.js`. Los estilos de la consola están al final de `static/css/app.css`.

### Nueva distribución

`.rejilla-mandos` usa CSS Grid: tres columnas desde el ancho por defecto, dos por debajo de 900 px y una por debajo de 560 px. Cada mando es un recuadro con nombre, botón Inicio, valor y unidad, deslizador, extremos del recorrido y un campo numérico. La nota técnica larga va en un `<details>` con el resumen «i». Potencia, head/THD y PIP se dibujan en la misma rejilla como lectura, sin deslizador. La potencia sigue en «No disponible»: `brake_hp` es un punto de la curva de 60 Hz y no es una entrada.

En el navegador, con la métrica de dispositivo forzada, la rejilla midió tres pistas a 1280 px, dos a 800 px y una a 520 px. Los mandos editables quedaron en torno a 163 px de alto.

### Comportamiento de los controles

El valor grande se actualiza en el acto, con `formatoVisible`. El valor que viaja al motor está en `data-valor` y no se redondea al pintar. El campo numérico muestra como máximo dos decimales cuando no tiene el foco; si el operador escribe más, ese texto es el nuevo valor interno. Los extremos del deslizador siguen siendo recorrido de interfaz (`es_limite_operacional` falso), no límites de equipo.

### Restauración individual y general

«Inicio» copia el valor inicial de ese mando, actualiza el número y el deslizador, y dispara la evaluación. No mueve los demás. «Restaurar valores», en el encabezado, vuelve a dibujar todos los mandos desde la ficha y evalúa. No hay recarga de página. No quedan «Evaluar escenario» ni «Restaurar valores iniciales».

### Evaluación automática

Cada cambio programa el pedido a los 300 ms. Antes de enviarlo, la pantalla pasa a «EVALUANDO» y pierde el color anterior, con el texto «El estado anterior no corresponde a este pedido.» El cliente aborta la petición en curso. `pintar` ignora un cuerpo cuyo `evaluacion_id` no es el vigente. El cálculo llega con `explicar: false`. Si el código no es `ERROR_CALCULO` y la respuesta sigue vigente, se pide la explicación con `explicar: true` sin borrar la lámpara ya pintada. Si esa segunda respuesta no trae origen `ollama`, se mantiene el texto determinístico y la clasificación física.

### Formato numérico

`services/formato_numero.py` expone `formato_visible`. Redondea a dos decimales con el formato de Python y quita ceros finales. `60.0` queda `60`, `12.5` queda `12.5`, `45.567891` queda `45.57`, `0.123456` queda `0.12`. El JavaScript hace el mismo recorte sobre el texto ya redondeado a dos decimales, sin aplicar una expresión que se coma el cero de la parte entera. La API sigue enviando `valor` completo y añade `valor_visible`. En QF-084 el PIP interno conserva más de dos decimales y `valor_visible` coincide con `formato_visible`.

### Tratamiento de estados

La correspondencia nueva está en `services/estado_operacional.py` y sale solo de campos que el motor ya entrega: `estado_evaluacion`, `activada`, `aprobada_para_uso_operacional`, `limite_critico_validado`, `recomendacion_operacional_autorizada` y el id de la regla. No se inventaron umbrales para obtener los tres colores.

| Código | Color | Cuándo | Por qué no es otro |
|---|---|---|---|
| NORMAL | Verde | `recomendacion_operacional_autorizada` es verdadero y hay una regla activa aprobada de conformidad (RC-BES-03 o `conformidad_aprobada`), sin un crítico validado. | BES-jun deja la autorización en falso y RC-BES-03 en `pendiente_validacion`. Con la hoja real no aparece. La prueba usa un diccionario sintético, no un pozo. |
| INCIPIENTE | Amarillo | Está activa RC-BES-01 o RC-BES-02, o una regla con `alerta_temprana`, y esa regla no es un crítico validado. | En QF-084 a 60 Hz el caudal registrado de 10301 BFPD supera el máximo escrito de 10000 BFPD y se activa RC-BES-01. El máximo escrito no trae `limite_critico_validado`, así que no es CRÍTICO. El texto lo dice. |
| CRÍTICO | Rojo | Regla activa con `aprobada_para_uso_operacional` y `limite_critico_validado`, ambos verdaderos. | El motor de BES-jun no emite esa marca. Solo un diccionario sintético de prueba lo produce. |
| SIN_CLASIFICACION | Gris | RC-BES-03 sola, el aviso `fuera_de_dominio_observado`, o un cálculo preliminar sin regla que autorice un estado. `clasificacion_valida` queda en falso. | Comparar el texto de la hoja no es una conformidad aprobada. El intervalo observado de 56 Hz a 67 Hz no es un límite de equipo. QF-084 sin cambios queda aquí, con RC-BES-03 activa. |
| SIN_DATOS | Gris | Cualquier `estado_evaluacion` distinto de `completada_preliminar` que no sea un error de cálculo. El mensaje es «Evaluación no disponible: faltan datos.» | No se pinta como condición de la bomba. |
| ERROR_CALCULO | Gris | `entrada_invalida`, `error_interno` o `no_disponible`. El mensaje es «No fue posible completar el cálculo.» | Un rechazo de entrada, un fallo del motor o un tiempo de espera no se convierten en NORMAL, INCIPIENTE ni CRÍTICO. |

Si el pedido nuevo falla, la pantalla no conserva el rótulo del escenario anterior: ya se había sustituido por «EVALUANDO» y el error se pinta como «CÁLCULO NO COMPLETADO».

### Manejo de errores

Ollama no clasifica. El prompt le prohíbe llamar a la bomba normal, incipiente o crítica si ese no es el rótulo. `_compatible` descarta un texto que use esas palabras fuera de su código, que diga que la bomba está segura cuando el código no es NORMAL, o que invierta «dentro del texto» y «fuera». Una respuesta vacía, cortada por longitud o sin conexión deja el mensaje determinístico. La consola del operador no muestra el nombre del modelo, tokens ni infraestructura. El estado del servicio, el modelo y la prueba de conexión quedan en Configuración de IA.

### Pruebas y resultados

El 2026-10-21, `manage.py test tests.test_huc_web tests.test_consola` aprobó 28 pruebas en 7,339 s. Cubren la ausencia de «Evaluar escenario» y de «Restaurar valores iniciales» en el HTML, el botón «Restaurar valores», QF-084 inicial en `SIN_CLASIFICACION` con RC-BES-03 y sin clasificación válida, el paso a `INCIPIENTE` a 60 Hz sin pasar a `CRITICO`, `NORMAL` y `CRITICO` solo con diccionarios sintéticos, `SIN_DATOS` y `ERROR_CALCULO` sin esos tres códigos, el formato visible, la precisión interna del PIP, el debounce de 300 ms, `AbortController` y el descarte por `evaluacion_id`. El expediente BES-jun volvió a aprobar 182 pruebas en 19,66 s. El SHA-256 del Excel de trabajo y del original se comprobó en la misma batería web y sigue en `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`.

En el navegador, QF-084 cargó en «SIN CLASIFICACIÓN OPERACIONAL», con 63 Hz y TVD 2653,18 ft en el valor grande. No había botón de evaluar ni de restaurar el mando con el texto antiguo. Había dos botones Inicio y tres lecturas sin deslizador.

### Limitaciones pendientes

Siguen sin dibujarse caudal, presión de sensor, THP, temperatura, API y BS&W. No hay límite de variador que la consola pueda hacer cumplir. NORMAL y CRÍTICO no salen de un pozo real de BES-jun. La explicación del modelo puede tardar y, si no llega, el operador lee el texto determinístico más el aviso de que el asistente no está disponible. No hay telemetría en vivo. RB-1521 y RB-IA-2191 siguen fuera del selector.

## Menú lateral — Estado de pozos

### Sustitución del indicador de Ollama

El menú lateral de `templates/base.html` mostraba «Ollama responde», el nombre del modelo y el dataset de sesión. Eso es administración del asistente, no el estado de una bomba. Ese bloque se eliminó. El registro en `/administracion/` tampoco repite el servicio, el modelo ni el dataset seleccionado. Esos datos quedan en Configuración de IA: si el servicio responde, el modelo elegido, si está instalado, el tope de tokens, el tiempo máximo y los botones «Probar conexión» y «Prueba técnica controlada».

La consola deja de usar el enlace «Administración» a la derecha del encabezado. En su lugar, a la izquierda, hay un botón con icono de menú (`#alternar-menu`) que oculta o muestra el panel. Dentro del panel sigue un enlace de texto hacia el registro, para no perder el camino.

### Origen de los estados

`GET /api/consola/estados/` recorre `listar_pozos()`, es decir los `pozo_rotulo` de cada `integracion/pozos.json`. Hoy son los cinco de BES-jun. No hay una lista fija en la plantilla. RB-1521 y RB-IA-2191 no tienen pozos en su ficha y no aparecen.

Cada fila llama a `evaluar_pozo` con los controles vacíos y `explicar` en falso. El motor lee la hoja. `clasificar` aplica la misma correspondencia de la consola. No se lee `resultados_deterministicos.csv` para pintar la luz: ese archivo trae magnitudes calculadas, no un código NORMAL, INCIPIENTE o CRÍTICO, y es un resultado histórico. No hay telemetría. La nota de la lista lo dice.

### Correspondencia entre códigos y colores

| Luz | Código | Cuándo |
|---|---|---|
| Verde | NORMAL | Solo si `clasificacion_valida` es verdadero y el tono es `normal`. |
| Amarillo | INCIPIENTE | Igual, con tono `incipiente`. En QF-084 aparece si el escenario activa RC-BES-01 o RC-BES-02, por ejemplo al bajar la frecuencia a 60 Hz. No sale del valor de la ficha. |
| Rojo | CRÍTICO | Igual, con tono `critico`. BES-jun no lo produce: haría falta una regla aprobada y `limite_critico_validado`. |
| Gris | Cualquier otro | `clasificacion_valida` es falso. Incluye SIN CLASIFICACIÓN OPERACIONAL, falta de datos, cálculo no completado y la espera «EVALUANDO». No es una falla de la bomba. |

Con la ficha tal cual, los cinco pozos quedan en `SIN_CLASIFICACION` y la luz es gris. RC-BES-03 activa no se pinta de verde.

### Actualización dinámica

`static/js/pozos_menu.js` pide la lista al cargar, sin recargar la página. Al elegir otro pozo en la consola, o al pulsar su identificador en el menú, se marca la fila y se cargan sus mandos. Cuando el motor devuelve un resultado, `consola.js` publica `huc-estado` con el código ya clasificado. La explicación de Ollama no cambia la luz. Durante el cálculo la luz de ese pozo pasa a gris con el rótulo «EVALUANDO», para no dejar el color anterior sobre el escenario nuevo.

La lista tiene `overflow-y: auto` y una altura máxima propia, para que muchos pozos no empujen los enlaces del menú.

### Diferencia entre estado inicial y simulado

El endpoint solo describe el escenario inicial. Si el operador mueve un mando, el navegador guarda en `sessionStorage` (`huc.escenarios`) la ficha de ese pozo con origen `simulacion`. Al volver a pintar, esa ficha sustituye únicamente a ese identificador. Restaurar los valores de la ficha borra esa entrada y la luz vuelve al escenario inicial. Un pozo no escribe la ficha de otro. Nada se guarda en el Excel ni en `pozos.json`. El tooltip distingue la fuente: ficha inicial, simulación de esta sesión, o evaluación en curso.

### Pruebas realizadas

El 2026-10-21, `manage.py test tests.test_huc_web tests.test_consola` aprobó 29 pruebas. Comprueban que el menú de `/evaluaciones/` y la consola muestran «ESTADO DE POZOS» y no «Ollama responde» ni el nombre del modelo, que Configuración de IA sigue mostrando el modelo y la prueba de conexión, que un Ollama caído no tumba la consola ni el registro, y que `/api/consola/estados/` devuelve los cinco pozos reales, QF-084 en `SIN_CLASIFICACION` con luz no válida, sin llamar al asistente. El SHA-256 del Excel no cambió.

### Limitaciones pendientes

La simulación solo vive en el navegador de esa sesión. Al cerrarla, el menú vuelve a las luces de la ficha. No hay un histórico de escenarios simulados. NORMAL y CRÍTICO siguen sin salir de un pozo real de BES-jun. El gris inicial no debe leerse como «la bomba está bien».

## Vinculación de los potenciometros con las reglas

### Reglas encontradas

El catálogo de BES-jun tiene cuatro reglas. Tres están implementadas en `comparar_caudal_con_limites`. RC-BES-04 no tiene función y su estado es `no_evaluable`. Ninguna está aprobada para uso operacional. `reglas.json` describe el catálogo; no se ejecuta.

### Potenciometros

Se eliminaron la profundidad TVD, la potencia y el head como mandos. No participan en RC-BES-01, 02 ni 03. El PIP y el THD quedan como lecturas del balance, no como entradas.

Se conservó la frecuencia y se incorporó el caudal de operación. Los dos están en las variables requeridas de las reglas ejecutables y el contrato los acepta como variables operacionales. Los límites escritos y la base de 60 Hz no son mandos.

El recorrido de la frecuencia es 56 Hz a 67 Hz, las frecuencias escritas en las hojas. El recorrido del caudal es la curva tabulada a 60 Hz escalada con la razón de `limites_a_frecuencia`. Así se puede cruzar el máximo escrito sin inventar un porcentaje del slider. El servicio está en `services/rule_control_registry.py`. La plantilla no lista los mandos.

### Estados

Al cargar, cada pozo se compara con la medición registrada de su hoja. Los cinco quedan en NORMAL: RC-BES-03, caudal entre el mínimo y el máximo inclusive. Eso no autoriza la operación. `recomendacion_operacional_autorizada` sigue en falso.

INCIPIENTE es RC-BES-01 o RC-BES-02. No hay zona crítica en el expediente, así que CRÍTICO solo aparece en un diccionario sintético de prueba. Se quitó el rótulo «SIN CLASIFICACIÓN OPERACIONAL» y los textos de telemetría, de falta de autorización y de la regla no aprobada que la pantalla repetía.

La luz del menú sale de esa misma clasificación. Una simulación de un pozo no cambia la de otro. Ollama no pinta la luz.

### Pruebas

El 2026-10-21, `manage.py test tests.test_huc_web tests.test_consola` aprobó 30 pruebas. Incluyen la matriz de controles, el borde 10 500 / 10 501 BFPD en QF-084, la vuelta a NORMAL, el rechazo de la TVD como mando, los cinco pozos en NORMAL al inicio y la conservación del SHA-256 del Excel.

### Pendiente

CRÍTICO no es calculable con BES-jun. RC-BES-04 no se evalúa. CT-06, CT-08 y CT-03 siguen abiertas. Presión, temperatura, API y BS&W no tienen regla ejecutable y no se dibujan. RB-1521 y RB-IA-2191 siguen sin pozos en la consola.

## L. Próxima etapa

1. Dejar esta versión en uso local y no promover RB-1521 ni RB-IA-2191 hasta una decisión explícita sobre P-14.
2. Si se quiere simular, implementar WEB-01 sobre el contrato que ya existe, sin tocar las ecuaciones.
3. Cuando haya una confirmación de instrumentación del sensor, el cambio del signo del PIP se hace en el expediente, con pruebas, y la web solo dejará de mostrar la reserva si el documento de discrepancias deja de marcar CT-03.
4. No añadir gráficas ni una base vectorial hasta que haya una serie y una pregunta que el recorte actual no pueda responder.

El servidor de desarrollo, si sigue el proceso arrancado durante esta implementación, está en `http://127.0.0.1:8000/`. Para volver a levantarlo, la orden es la del apartado E.
