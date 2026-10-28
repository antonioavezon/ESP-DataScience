# Arquitectura de la aplicación

## Frontera

Django vive en `web/`. El motor, los esquemas y los datos siguen en el expediente. `services/huc_adapter.py` añade `datasets/en_uso/BES-jun/src` a `sys.path` solo en el momento de llamar a `evaluar_solicitud`. No hay una segunda implementación de las ecuaciones.

`asesor-esp` no participa. DEC-004 sigue en pie: no se copian las fórmulas de BES-jun a ese paquete.

## Módulos

| Módulo | Responsabilidad |
|---|---|
| `services/dataset_registry.py` | Recorre las tres carpetas del ciclo y arma una ficha por expediente que tenga `dataset.md` o un manifiesto. El identificador sale del manifiesto y, si no hay manifiesto, del campo de `dataset.md`. |
| `services/huc_adapter.py` | Elige el adaptador. Hoy solo BES-jun, y solo si tiene motor y contratos, usa `AdaptadorBesJun`. El resto recibe `AdaptadorSinMotor`. Las vistas no repiten esa condición. |
| `services/ollama_client.py` | HTTP a `/api/tags` y `/api/chat`. Una respuesta 200 con contenido vacío, JSON inválido o modelo ausente no se da por buena. |
| `services/technical_context.py` | Arma el mensaje de sistema con la definición verificada de PIP, extractos de archivos existentes y, si se eligió un pozo, la fila del CSV. |
| `apps/core` | Dashboard y página Acerca. |
| `apps/datasets` | Lista, ficha y pozo. La selección queda en la sesión. |
| `apps/evaluaciones` | Formulario operacional y presentación del JSON que devuelve el motor. |
| `apps/asistente_ia` | Consulta y panel de límites de la sesión. |

## Flujo de una evaluación

1. La sesión indica el dataset. Si nadie eligió uno, se toma el primero de `en_uso`.
2. El pozo tiene que estar en `integracion/pozos.json` de esa ficha.
3. Los campos vacíos no se envían. Un texto no numérico responde 400 y no llama al motor.
4. Las únicas mediciones admitidas son las de `VARIABLES_OPERACIONALES` del contrato, con la unidad canónica.
5. `evaluar_solicitud` valida el esquema, calcula o devuelve `entrada_invalida` / `error_interno`.
6. La vista guarda un subconjunto JSON en la sesión: estado, reglas, advertencias, errores y valores de modelo. No guarda curvas ni trazas.

## Flujo de una consulta

1. `technical_context.mensajes` separa el sistema del texto del operador.
2. El cliente comprueba que el modelo elegido esté en `/api/tags`. Si no está, se detiene.
3. `think` va en falso. Si aun así llega `message.thinking`, se descarta y no se copia a la plantilla.
4. `done_reason=length` marca la respuesta como incompleta.

## Sesión y base local

SQLite en `web/db.sqlite3` solo guarda sesiones de Django. No hay tablas científicas. El archivo está en `.gitignore`.

## Extensión

Un dataset nuevo entra al registro por estar en una de las tres carpetas y tener `dataset.md`. Para poder evaluarlo hace falta un adaptador registrado en `adaptador_para` que llame a su propio motor. Mientras no exista, la ficha se ve y la ejecución permanece deshabilitada, con la causa escrita en la ficha.
