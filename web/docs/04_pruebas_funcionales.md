# Pruebas de la aplicación

Entorno: Fedora 43, Python 3.14.8, Django 6.0.9. Las órdenes se ejecutaron el 2026-10-21.

## Expediente BES-jun, antes de crear `web/`

```bash
cd /home/antonio/projects/HUC/datasets/en_uso/BES-jun
PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m pytest -q --tb=line
```

Resultado: 182 pruebas aprobadas en 20,42 s.

## Expediente BES-jun, después

La misma orden. Resultado: 182 pruebas aprobadas en 20,08 s. No se modificó ninguna prueba del expediente.

## Django

```bash
cd /home/antonio/projects/HUC/web
/home/antonio/projects/HUC/.venv/bin/python manage.py check
/home/antonio/projects/HUC/.venv/bin/python manage.py test tests.test_huc_web
```

`check` no reportó problemas. La suite tiene 16 pruebas y terminó bien en 1,600 s en la última ejecución. Cubren, agrupadas, los veinte puntos pedidos: arranque y rutas, dashboard, registro, BES-jun, pendientes sin resultados, lectura del CSV, rechazo de texto en una medición, campo en blanco distinto de cero, adaptador sobre `evaluar_solicitud` (QF-084, `completada_preliminar`, RC-BES-03 activada, recomendación operacional en falso), Ollama simulado disponible y caído, modelo ausente, timeout, JSON inválido, respuesta vacía, respuesta con `done_reason=length`, descarte de `thinking`, contexto de PIP, rutas ajenas al registro y SHA-256 del Excel.

La suite simulada no necesita el demonio. La llamada real quedó fuera de esa suite para que un Ollama apagado no la haga fallar.

## HTTP contra el servidor de desarrollo

`runserver` en `127.0.0.1:8000`. Códigos obtenidos con curl:

| Ruta | Código |
|---|---|
| `/`, `/datasets/`, `/datasets/BES-jun/`, `/datasets/RB-1521/`, `/datasets/RB-IA-2191/`, `/datasets/BES-jun/pozos/QF-084/`, `/evaluaciones/`, `/asistente/`, `/asistente/configuracion/`, `/acerca/` | 200 |
| `/datasets/no-existe/` | 404 |

Un POST a `/evaluaciones/ejecutar/` con el pozo QF-084 y sin mediciones respondió, tras la redirección, `completada_preliminar`, la regla RC-BES-03 y `pendiente_validacion`.

## Navegador

Se abrió `http://127.0.0.1:8000/` en el navegador automatizado. En 1280 px de ancho el menú queda a la izquierda y el contenido a la derecha, sin desborde horizontal. En 390 px el marco pasa a una columna y tampoco desborda. CSS y JS respondieron 200. Se recorrieron Datasets, la ficha BES-jun, QF-084, Evaluaciones y Configuración de IA. El selector mostró el modelo Instruct y la tabla avisó del consumo de tokens en los modelos con capacidad `thinking`. No se vieron respuestas 500 en el registro del servidor.

## Huella del Excel

Después de la evaluación por HTTP, el SHA-256 de `entrada/BES_jun.xlsx` y el de `fuentes/originales/Copia de FINAL BES-jun.xlsx` seguían siendo `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`.
