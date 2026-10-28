# Auditoría de integración para la aplicación web

Fecha: 2026-10-21. Entorno: Fedora 43, Python 3.14.8 del entorno `.venv` del repositorio. No existía un directorio `web/` ni un proyecto Django. `asesor-esp/` es un esqueleto de otro motor, en unidades SI, y no consume el paquete de BES-jun (DEC-004). El directorio raíz de HUC no es un repositorio Git (`git status` responde que no es un repositorio). No había cambios que revertir.

La línea base del expediente, ejecutada antes de crear esta aplicación, fue 182 pruebas aprobadas en 20,42 s (`PYTHONPATH=src` desde `datasets/en_uso/BES-jun`).

## Qué puede consultarse directamente

| Fuente | Qué contiene | Uso en la interfaz |
|---|---|---|
| `datasets/en_espera/`, `en_uso/`, `procesadas/` | Ciclo de cada expediente. `procesadas/` está vacío. | Registro. No se promueve ningún dataset. |
| `datasets/en_uso/BES-jun/dataset.md` | Identificador, estado de validación pendiente, SHA-256 del Excel. | Ficha. |
| `datasets/en_espera/RB-1521/dataset.md` y `RB-IA-2191/dataset.md` | Estado «En espera». Sin copia de trabajo y sin orden de abrir el libro. | Ficha pendiente. Sin pozos ni resultados. |
| `integracion/manifiesto.json` | `dataset_id` BES-jun, versión 0.4.2, contrato 1.3.0, catálogo 1.1.0, cinco pozos, cuatro reglas, `reglas_aprobadas` vacío, estado `validacion_pendiente`. | Resumen y advertencias. |
| `integracion/pozos.json` | Cinco fichas. Identidad `provisional`. Curva de 60 Hz con campos extra (`brake_hp`, `eff_numero`). | Lista de pozos. La curva de la ficha no se envía como curva de escenario. |
| `integracion/variables.json` | Catálogo con unidad, tipo y procedencia. | Tabla de variables. |
| `integracion/reglas.json` | RC-BES-01, 02 y 03 en `pendiente_validacion`. RC-BES-04 no está aprobada. `aprobada_para_uso_operacional` es falso. | Tabla de reglas, sin tratarlas como autorización. |
| `integracion/contrato_entrada.schema.json` y `contrato_salida.schema.json` | Contratos 1.3.0. | El adaptador arma la solicitud y no reimplementa el esquema: llama a `validar` dentro de `evaluar_solicitud`. |
| `data_procesados/resultados_deterministicos.csv` | Columnas reales: `hoja`, `pozo`, pares `nombre` y `nombre__hoja` para `sg_60`, `sg_temperatura`, `densidad_lb_gal`, `gradiente_psi_ft`, `pip_ft`, `thp_ft`, `friccion_ft`, `thd_total_ft`, `caudal_a_producir_bfpd`, y `caudal_medido_bfpd`. Cinco filas, una por pozo. | Consulta. Un campo vacío se muestra como «No disponible», no como cero. |
| `docs/discrepancias_cientificas.md` del expediente | CT-03 (signo del PIP), CT-05, BS&W, identidad, caché, `TODAY()`. | Advertencias citadas, no corregidas desde la web. |
| `integracion/capa_linguistica.md` | El texto del asistente solo puede explicar el JSON. No inventa límites ni ordena cambiar la frecuencia. | Entra al contexto con su ruta de origen. |
| `docs/arquitectura_funcional.md`, `estado_proyecto.md`, `bloqueos.md`, `decisiones.md`, `hoja_de_ruta.md`, `guia_procesamiento_datasets.md` | La aplicación gráfica y el modelo de lenguaje figuraban como no empezados. P-14 sigue abierta. BES-jun no se mueve a `procesadas`. | Texto de «Acerca». |
| Ollama en `http://127.0.0.1:11434/api/tags` | El servicio respondió. Está instalado `qwen3:4b-instruct-2507-q4_K_M`. También hay otros modelos locales, entre ellos `qwen3:4b`, cuya capacidad incluye `thinking`. | El selector lista lo instalado. No descarga ni cambia el servicio. |

## Qué funciones se reutilizan

El motor público está en `datasets/en_uso/BES-jun/src/evaluacion/motor.py`: `evaluar`, `evaluar_solicitud` y `evaluar_json`. La aplicación solo usa `evaluar_solicitud`. Esa función valida el contrato, calcula con los modelos ya escritos y, si hay una excepción, devuelve `error_interno` con `incidente_id` sin filtrar el traceback al operador.

Las mediciones que el operador puede enviar, según `contratos.py`, son `caudal_operacion_bfpd` (BFPD), `frecuencia_hz` (Hz), `presion_sensor_psi` (psi), `thp_psi` (psi), `api_deg` (°API), `bsw_numero` (fracción) y `temperatura_c` (°C). Los parámetros de ficha (`limite_minimo_bfpd`, `curva`, TVD, etapas, etc.) están protegidos en modo operacional. La interfaz no los ofrece.

Una solicitud sin variables usa la hoja. Un campo de formulario en blanco no se convierte en cero: se omite.

No hay adaptador para RB-1521 ni para RB-IA-2191. Su registro solo lee `dataset.md`. No se abre el `.xls` ni el `.xlsx`.

## Limitaciones que la interfaz debe mostrar

- Ninguna regla está aprobada. `recomendacion_operacional_autorizada` permanece en falso.
- La identidad Cluster / Pozo es provisional.
- El PIP que sale de la celda no está validado físicamente (CT-03). El gradiente de la hoja está rotulado `psi*ft` y la cuenta es de psi/ft. La web no cambia el signo ni la unidad.
- CT-01 a CT-10 siguen abiertas, según el manifiesto.
- Reproducir la caché de Excel no es una validación experimental.
- El rango de frecuencia observado no es un límite operacional.
- `asesor-esp` no se usa como motor de esta versión.

## Qué faltaba

Cliente HTTP de Ollama, registro de datasets, vistas, plantillas, pruebas de la aplicación y la documentación de `web/`. Esta auditoría es el primer archivo de esa documentación. La implementación que sigue no copia el motor ni los CSV dentro de `web/`.
