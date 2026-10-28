# Evaluación del asistente lingüístico HUC

Artefactos de la batería versionada `web/tests/eval_asistente/catalogo_v1.json` (71 casos, grupos A–I).

## Cómo ejecutar

Desde `web/`, con el entorno Django del proyecto:

```bash
PYTHONPATH=. DJANGO_SETTINGS_MODULE=config.settings python -c \
  "import django; django.setup(); from tests.eval_asistente.correr_eval import correr; print(correr(etiqueta='local')['pct_exito'])"
```

La corrida mock no llama a Ollama: usa un cliente fijo que devuelve JSON `{resumen, explicacion}` para medir intención, contexto, contrato y render.

## Archivos

| Archivo | Contenido |
|---|---|
| `antes_intencion.json` | Tras el contrato v1.0 y antes de ampliar intención/adversarial (73.24 % éxito) |
| `despues.json` | Tras mejoras de intención y seguridad (100 % mock, 71/71, contratos 71/71) |
| `real_llm_subset.json` | 4 consultas reales contra Ollama en Docker |

No se incorporan a las imágenes Docker.
