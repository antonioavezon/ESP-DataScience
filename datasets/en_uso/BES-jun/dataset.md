# Expediente BES-jun

**Estado:** validación pendiente (cierre computacional de esta pasada; sin aprobación operacional). Sigue en `en_uso`. No está Completo.

**Identificador:** `BES-jun`

**Original:** `Copia de FINAL BES-jun.xlsx`  
Copia íntegra: `fuentes/originales/Copia de FINAL BES-jun.xlsx`  
SHA-256: `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`  
MD5: `ba89f317f505f321c496e44ab5046104`  
Tamaño: 329308 bytes.

**Copia de trabajo:** `entrada/BES_jun.xlsx`  
Mismo SHA-256. El libro no se guarda al leerlo. El original no se renombra ni se edita.

Este expediente es el único en `datasets/en_uso/`. No forma parte del tablero de asesor-esp. P-14 sigue sin respuesta. El orden oficial sigue siendo D1 y después D2. RB-1521 y RB-IA-2191 no se abrieron.

## Contenido

| Ruta | Uso |
|---|---|
| `entrada/BES_jun.xlsx` | Copia de trabajo |
| `src/` | Lectura, fórmulas de este libro, estadística, figuras, informe y PDF |
| `notebooks/00_inventario_y_fuentes.ipynb` … `06_hallazgos_y_reglas_candidatas.ipynb` | Cuadernos del cierre, ejecutados |
| `notebooks/00_inventario_y_trazabilidad.ipynb` … `04_modelo_deterministico.ipynb` | Cuadernos de numeración repetida: objetivo distinto, no duplicados (`docs/revision_notebooks_auditoria.md` §7) |
| `data_procesados/` | Perfil, estadísticas, survey y registro de transformaciones |
| `tests/` | 182 pruebas en el AutoTest del 2026-10-21 (`logs/autotest_reporte.md`). Contrato 1.3.0. Motor 0.4.2. La auditoría de PIP está en `docs/informe_auditoria_pip_BES-jun.md` |
| `docs/` | Ficha Maestra, diccionario, catálogo de variables, reglas, auditoría y consultas técnicas |
| `integracion/` | Paquete para la aplicación: manifiesto, pozos, variables, modelos, reglas y contratos |
| `reports/informe_analisis_BES-jun.md` | Informe |
| `reports/informe_analisis_BES-jun.html` | El mismo informe en HTML |
| `reports/figuras/` | Gráficos de este libro |
| `pdf/informes/informe_analisis_BES-jun.pdf` | Informe en carta |
| `pdf/notebooks/` | HTML y PDF de los 12 cuadernos, generados del cuaderno completo y verificados (`docs/procedimiento_exportacion_cuadernos.md`) |
| `requirements.txt` | Versiones usadas |

Los cuadernos `05_evaluacion_por_pozo.ipynb` y `06_hallazgos_y_reglas_candidatas.ipynb` se reescribieron porque el cierre pide esos nombres. Los cuadernos 00 a 04 de la pasada anterior conservan sus nombres viejos.

El catálogo común sigue en `../../../docs/trazabilidad_ecuaciones.md`.

## Qué no es

No es un motor para otros Excel. No hay pronóstico validado. Las reglas siguen candidatas. No se mueve a `datasets/procesadas/` hasta la aprobación del usuario.
