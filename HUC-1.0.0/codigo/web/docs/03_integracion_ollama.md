# Integración con Ollama

## Valores

Salen del entorno, con estos defaults si la variable no está definida:

| Variable | Default |
|---|---|
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | `qwen3:4b-instruct-2507-q4_K_M` |
| `OLLAMA_TIMEOUT_S` | 60, acotado entre 5 y 120 |
| `OLLAMA_NUM_PREDICT` | 512, acotado entre 32 y 1024 |

La sesión puede guardar otro modelo, otro tope de tokens y otro tiempo. Eso no cambia el proceso de Ollama ni un servicio systemd. No hay botones para instalar, borrar o descargar modelos.

## Endpoints

- `GET /api/tags` para el estado y la lista.
- `POST /api/chat` con `stream: false`, `think: false` y `options.num_predict`.

El cliente usa `httpx` y `trust_env=False`, para no salir por un proxy hacia otro host. El timeout es el de la sesión.

## Cuándo no es éxito

- Error de conexión o timeout.
- Cuerpo que no es JSON.
- El modelo pedido no está en la lista. No se sustituye por otro.
- `message.content` vacío o en blanco. Si había `thinking`, se cuenta como descartado y no se enseña.
- `done_reason` igual a `length`: el texto parcial se muestra con el aviso de que no es una conclusión terminada.

## Contexto

`technical_context.py` siempre incluye:

> PIP = Pump Intake Pressure: presión del fluido en la entrada de la bomba electrosumergible.

La marca es `definicion_verificada` y la fuente queda nombrada. Para BES-jun se añaden, si existen, extractos de `integracion/capa_linguistica.md`, `docs/discrepancias_cientificas.md` y `integracion/manifiesto.json`, más las limitaciones del manifiesto y la fila del CSV del pozo elegido. No hay base vectorial. Otro recuperador puede sumar bloques al mismo diccionario sin cambiar las vistas.

El texto del operador viaja como `user`. El sistema le dice al modelo que ignore pedidos de cambiar las reglas o de mostrar un razonamiento interno.

## Modelos con razonamiento

Si `/api/tags` declara la capacidad `thinking`, el panel avisa que pueden gastar tokens y alargar la espera. El operador puede elegirlos. La plantilla solo pinta `contenido`.

## Comprobación real del 2026-10-21

Ollama respondió en `/api/tags`. El modelo inicial estaba instalado. Una consulta enviada por `POST /asistente/enviar/`, con QF-084 en el contexto, devolvió en el bloque visible:

> PIP es la presión del fluido en la entrada de la bomba electrosumergible.

La página marcó la respuesta como finalizada. El bloque de la respuesta no contenía una cadena de razonamiento. La duración de esa petición HTTP, incluida la redirección, fue de unos 8,8 s.
