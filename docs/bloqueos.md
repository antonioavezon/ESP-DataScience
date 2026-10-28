# Bloqueos

El archivo `Copia de FINAL BES-jun.xlsx` sí está en el proyecto. No hay bloqueo por archivo ausente.

## Bloqueos técnicos de esta iteración

| ID | Qué falta | Efecto |
|---|---|---|
| B-01 | Puerta de fórmulas: trazabilidad reconciliada, formulación base con unidades, supuestos, dominio y parámetros, y G1 | El motor determinístico general sigue bloqueado |
| B-02 | Significado confirmado de BS&W: la unidad escrita es «%» y la fórmula usa el número como fracción | No se convierte el 0.9755 |
| B-03 | Definición, fuera de la celda, de 0.00066, 0.0000003, 15.556, 8.33, 0.052, C=120 y el exponente 4.8566 | Se transcriben; no se sustituyen por los del PDF |
| B-04 | Serie temporal y variable objetivo de pronóstico | No hay predicción |
| B-05 | Curva de fabricante distinta de la tabla escrita en la hoja, y explicación de la columna EFF | No se dibuja una curva de catálogo ni se llama BEP al «Cono de eficiencia» |
| B-06 | P-14 sin respuesta del responsable del alcance. Registro en `docs/decisiones_pendientes.md`: respuesta vacía, fecha de respuesta vacía, responsable aún el Remitente del plan | El orden del tablero no cambia. D1 sigue siendo RB-1521 y D2 sigue después. BES-jun no entra al tablero ni sustituye a D1 |
| B-08 | El libro no declara si la llave es Cluster, Pozo o el nombre de la hoja | Cada hoja se procesa sola. No se fusionan |
| B-09 | En el XLSM, `J64` suma donde el dibujo de Pwf inferido resta. Lo registró la revisión de ecuaciones | Esa fórmula no se usa en BES-jun y queda pendiente |
| B-07 | `xlrd` 2.x no lee `.xls` | En este entorno se usó `xlrd==1.2.0` para poder leer D1 más adelante. El `requirements.txt` de `asesor-esp` pide `xlrd>=2.0.1`, que no abre D1 |

## Lo que sí quedó cerrado

La copia de trabajo y la de `fuentes/originales/` conservan el SHA-256 del original. El original de la raíz no se reescribió.
