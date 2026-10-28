# Inventario de fuentes

Fecha de lectura: 2026-10-17. Sistema: Fedora Linux 43 (Workstation). Python del entorno: 3.14.8.

Los archivos de la raíz no se modificaron. Las copias de `fuentes/originales/` tienen el mismo SHA-256 que el archivo de la raíz. La copia de trabajo del expediente activo es `datasets/en_uso/BES-jun/entrada/BES_jun.xlsx` y conserva el mismo SHA-256.

`trabajo2.md` y `asesor-esp/trabajo.md` tienen el mismo MD5: `f6a883a720ad3f4da07ab45363dc5522`.

## Archivos y hashes

| Archivo | Bytes | SHA-256 | MD5 | Papel en esta iteración |
|---|---:|---|---|---|
| `Copia de FINAL BES-jun.xlsx` | 329308 | `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85` | `ba89f317f505f321c496e44ab5046104` | Primer dataset. No está en la tabla §4.1 de `trabajo2.md`. |
| `RB-1521-PY-121120.xls` | 84480 | `3c5043da6255c36c2c4270e465b4ee20dd7e6de534e58b8e84b42d350edf8808` | `a2dcc88b6b1ee8a82db9fdad29b5affa` | D1 del plan. MD5 coincide con `asesor-esp/data/raw/README.md`. No se leyeron sus filas aquí. |
| `RB-IA-2191-Data.xlsx` | 15491 | `908149f26e7560dc6bce75dc0268560e93a05d88b685218856b738dea39d9f08` | `8c82a502b1e10d8db9e69b7f6f6918b4` | D2 del plan. MD5 coincide. No se mezcló con BES-jun. |
| `Modelo_Sensorless_PIP_ESP_Set_Ecuaciones.docx` | 43143 | `4ef527d9b2cafdb1ee689093af6883763c4c864d5dc863b3d1b7aaf51fbb5ccc` | `e39d771a6887be370e08f0bdcff6d93b` | E1. Especificación algebraica. |
| `Modelo_Sensorless_PIP_ESP_Set_Ecuaciones (1).docx` | 43143 | igual a E1 | igual a E1 | Duplicado exacto. |
| `Modelo_Sensorless_PIP_ESP_Set_Ecuaciones (2).docx` | 43143 | igual a E1 | igual a E1 | Duplicado exacto. El plan solo citaba E1 y E1b. |
| `Modelo_Sensorless_PIP_ESP_Set_Ecuaciones (3).docx` | 43143 | igual a E1 | igual a E1 | Duplicado exacto. |
| `Copia de Copia de Ecuaciones  _.xlsm` | 142127 | `1e9eb80131a48abd5054ad4f39df25c0c3917c8734b7094f21075c3539413941` | `4c4bcb0b286875276ecfbd8b2399dc63` | X1. Fórmulas leídas del XML. VBA presente y no ejecutado. |
| `paper_sensorless - v2.docx` | 34831 | `9eeddb2f155972183b55c19487c3afbe464623f68ad410305cd9c64542e86e69` | `d88056c6c2276fa63d12834f44118d9f` | A1. Contexto. Sus métricas no son resultados de BES-jun. |
| `004-ESPdesign.pdf` | 320563 | `9d14c9db228f33653d0cc408b205b65818772f357bf7dd9253f905e9573991ec` | `886d6f65af4868f5ec25a5ece5fb8860` | R1. Seis páginas. Contexto de diseño. |
| `trabajo.md` | 27313 al inicio | `57d97df970ce6ebe1b901822de101d0379c13e82b5a19e8ab4b629965c7e8dbe` al inicio | — | Plan rector de la raíz. El coordinador lo actualizó después del inventario. |

## Duplicados de ecuaciones

Los cuatro DOCX `Modelo_Sensorless_PIP_ESP_Set_Ecuaciones*.docx` son el mismo archivo byte a byte. Se usa uno. Los otros quedan registrados.

## XLSM sin ejecutar macros

Hojas visibles: `Hoja1`, `METODO`, `Metodo Ordenado`, `Hoja2`, `Prueba Sesnorless`. Hay `vbaProject.bin`. No hay nombres definidos. El detalle de celdas está en `logs/extractos_coordinador/xlsm_celdas.txt`.

## BES-jun, solo estructura

Cinco hojas visibles, una por clúster. El pozo escrito en la celda `Pozo` no coincide con el nombre de la hoja. No es una serie diaria. El detalle está en `docs/diccionario_datos_BES_jun.md`.

## Libros que esta iteración no analiza

| Archivo | Lo que se comprobó | Lo que no se hizo |
|---|---|---|
| `RB-1521-PY-121120.xls` | Existe, MD5 del plan, 84480 bytes | No se leyeron filas ni se usó como reemplazo |
| `RB-IA-2191-Data.xlsx` | Existe, MD5 del plan. El plan dice una hoja y 28 días | No se leyeron filas |

El plan `trabajo2.md` §4.2 describe columnas de D1 y D2. Esas descripciones no se revalidaron en esta iteración y no se aplican a BES-jun.
