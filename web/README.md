# Aplicación web HUC

Interfaz local, en Django, para consultar los expedientes que ya están en el repositorio. El cálculo sigue en `datasets/en_uso/BES-jun/src`. Esta carpeta no guarda copias de los libros ni de los CSV.

## Qué hace

- La página inicial es una consola de bomba ESP: pozo, estado y mandos de simulación.
- El registro de datasets, Ollama y el resto de la administración están en `/administracion/`.
- Abre BES-jun: pozos, variables, reglas y el CSV determinístico ya generado.
- Deja RB-1521 y RB-IA-2191 como pendientes, sin leer sus libros.
- Ejecuta `evaluar_solicitud` solo cuando el expediente tiene motor y contratos.
- Consulta Ollama en `127.0.0.1` y no muestra el razonamiento interno del modelo.

## Entorno

Fedora 43. El intérprete del proyecto es `.venv` en la raíz del repositorio (Python 3.14.8). Django 6.0.9 y httpx 0.28.1 se instalaron en ese mismo entorno. El `requirements.txt` de la raíz del repositorio no se modificó: las dependencias de la web están en `web/requirements.txt`.

El servidor de desarrollo debe escuchar solo en `127.0.0.1`.

## Arranque

Desde esta carpeta, con el entorno del repositorio:

```bash
cd web
python manage.py runserver 127.0.0.1:8000
```

Abrir `http://127.0.0.1:8000/`.

La instalación completa, las variables y el significado de cada comando están en `DESARROLLO.md`. La auditoría previa está en `docs/01_auditoria_integracion.md`.
