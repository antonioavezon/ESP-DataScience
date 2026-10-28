# AGENTS.md — Reglas comunes del proyecto asesor-esp

## Qué es este proyecto

Modelo determinístico para pozos con bombeo electrosumergible (ESP/BES), construido desde fórmulas físicas revisadas una por una y probado con cada dataset por separado. Es la base de un futuro asesor para operadores basado en un modelo de lenguaje (etapa posterior, solo diseño por ahora).

El plan completo, las fichas de tareas y el estado están en `trabajo.md`. Léelo antes de actuar.

## Reglas de oro

1. `trabajo.md` es la fuente de verdad. Solo el orquestador lo edita, y solo en §9 (tablero), §10 (preguntas) y §13 (registro).
2. `data/raw/` es de solo lectura. Nunca modificar, mover, renombrar ni sobrescribir los originales.
3. No inventar datos, valores ni fuentes. Si falta algo, usar un supuesto registrado (S-xx, `trabajo.md` §5.5) o detenerse y reportar la duda.
4. Toda fórmula implementada debe estar en `docs/formulas/catalogo.md` con estado "revisada" o "corregida" y citarse por su ID (F-xx) en el docstring.
5. Unidades SI dentro del motor. Toda variable física lleva sufijo de unidad: `pip_pa`, `q_m3s`, `prof_m`, `p_in_w`; en reportes, `pip_psi`, `q_bpd`. Las conversiones se hacen solo con `asesor_esp.unidades`.
6. Cada función nueva viene con su prueba. `pytest -q` y `ruff check .` deben pasar antes de pedir verificación.
7. Quien implementa no verifica: revisor y tester son agentes distintos del implementador.
8. Las reglas operativas sugieren qué evaluar; nunca ordenan acciones sobre el pozo.
9. Confidencialidad: no subir `data/raw/` a repositorios remotos ni enviar datos a servicios externos fuera de Cursor sin autorización (pregunta P-05).

## Stack

Python ≥ 3.11 · pandas · numpy · scipy · pydantic · pyyaml · xlrd (.xls) · openpyxl (.xlsx/.xlsm) · matplotlib · pytest · hypothesis · ruff.

## Comandos

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
pytest -q
ruff check .
```

## Estructura

- `src/asesor_esp/`: `unidades.py`, `datos/`, `modelo/`, `reglas/`, `salida/`, `cli.py`
- `tests/`: espejo de `src/` más `casos_dorados/`
- `data/`: `raw/` (solo lectura), `interim/`, `processed/`, `curvas/`, `casos/`, `escenarios/`
- `docs/`: bitácora, decisiones, conceptos, fórmulas, datos, verificaciones, validación, reportes, lenguaje
- `config/pozos/`: configuración por pozo

## Convenciones

- Idioma: español en documentación, comentarios y docstrings. Identificadores en español, sin tildes, en snake_case.
- Docstring de toda función física: qué calcula, fórmula (F-xx), unidades de entrada y salida, supuestos (S-xx) y fuente.
- Si una fórmula original tiene un error conocido (H-xx), implementar `modo="replica"` (reproduce el archivo) y `modo="corregido"`.
- Commits: `Txx.y: descripción breve`.
- Informes de verificación: `docs/verificaciones/Txx-revisor.md` y `docs/verificaciones/Txx-tester.md`.
