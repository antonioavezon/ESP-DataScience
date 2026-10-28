# Registro de decisiones (ADR)

Formato: contexto, decisión, consecuencias y estado (propuesta, aceptada, reemplazada).

---

## ADR-001 · Motor determinístico primero, capa de lenguaje después
- **Fecha:** 2026-10-17 · **Estado:** aceptada
- **Contexto:** el objetivo es un asesor para operadores de pozos ESP. El remitente definió un alcance de aprendizaje: entender la ESP, revisar las fórmulas y construir un conjunto de reglas antes de incorporar un modelo de lenguaje (GLM).
- **Decisión:** el cálculo vive en un motor determinístico trazable (fórmulas F-xx revisadas). El modelo de lenguaje, en una etapa posterior, solo redactará a partir del JSON del motor; nunca calculará.
- **Consecuencias:** cada número mostrado a un operador es reproducible y auditable. La capa de lenguaje puede cambiarse sin tocar el motor.

## ADR-002 · Un adaptador por dataset y un solo motor
- **Fecha:** 2026-10-17 · **Estado:** aceptada
- **Contexto:** cada Excel tiene columnas, unidades y problemas de calidad distintos, y debe procesarse por separado.
- **Decisión:** cada archivo tiene su adaptador hacia un esquema canónico común; el motor es único y lo que cambia por pozo es su configuración (`config/pozos/<id>.yaml`).
- **Consecuencias:** agregar un dataset nuevo no exige modificar el motor; los problemas de cada archivo quedan aislados en su adaptador.

## ADR-003 · Modo réplica y modo corregido
- **Fecha:** 2026-10-17 · **Estado:** aceptada
- **Contexto:** el prototipo Excel (X1) y la guía (R1) contienen errores y redondeos conocidos (Anexo B de trabajo.md), pero sus resultados son la única referencia numérica disponible.
- **Decisión:** las fórmulas con error conocido se implementan en dos variantes: `replica`, que reproduce el archivo original y sirve como prueba, y `corregido`, que es la que usa el motor.
- **Consecuencias:** se puede demostrar que el motor entiende el original y, a la vez, explicar cuantitativamente cada corrección.

## ADR-004 · BES-jun es un dataset distinto y, en esta iteración, el primero que se analiza
- **Fecha:** 2026-10-17 · **Estado:** propuesta
- **Contexto:** el plan v1.0 toma `RB-1521-PY-121120.xls` como D1 y deja abierta P-12 porque ese archivo tiene un solo pozo. En la raíz del proyecto está `Copia de FINAL BES-jun.xlsx`, que el encargo de esta iteración fija como primer dataset de análisis. Sus MD5 y SHA-256 no coinciden con D1 ni con D2.
- **Decisión propuesta:** tratar BES-jun por separado, con su propio adaptador cuando el esquema canónico exista. No usar sus filas para completar D1 o D2. No cambiar el orden D1 → D2 del tablero hasta que P-14 se responda.
- **Consecuencias:** el informe de esta iteración no valida el motor general. Las fórmulas transcritas de BES-jun quedan en borrador hasta la puerta G1.
