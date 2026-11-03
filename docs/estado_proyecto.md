# Estado del proyecto

Fecha: 2026-10-20.

## Hecho

- Expediente BES-jun en `datasets/en_uso/BES-jun`, con doce cuadernos, HTML y PDF verificados, informe regenerado y ficha maestra.
- Modelos de fluido, balance e intersección que reproducen la caché de las cinco hojas.
- Reglas candidatas ejecutables y un evaluador determinístico. QF-084, con el límite escalado a 63 Hz, queda en RC-BES-03. No hay recomendación operacional.
- Paquete `integracion/` con manifiesto, pozos, variables, modelos, reglas y contratos.
- 182 pruebas de pytest en el expediente, AutoTest del 2026-10-21. Contrato 1.3.0 y motor 0.4.2. La auditoría de PIP leyó las cinco hojas: la celda suma la columna aunque el sensor está más profundo, el rótulo del gradiente dice `psi*ft` y la fórmula no se cambió. CT-03 sigue abierta.
- Guía de procesamiento de datasets nuevos.

## En pruebas, no aprobado

- Las reglas RC-BES-01, 02 y 03 (`pendiente_validacion`).
- La afinidad Q ∝ f aplicada a los límites (CT-08).
- La identidad Cluster / Pozo.
- El signo del PIP, la fricción de Hazen-Williams y la unidad de BS&W.

## No empezado

- Análisis de RB-1521 y de RB-IA-2191.
- Catálogo central de pozos de más de un dataset.
- Motor único en unidades SI dentro de `asesor-esp` (el plan de esa carpeta lo prevé; P-14 sigue abierta).
- Aplicación gráfica conectada al paquete.
- Integración real con un modelo de lenguaje.
- Traslado de BES-jun a `procesadas`.

## Bloqueos visibles

CT-01 a CT-10 y P-14. No se dan por cerrados.


---

## Actualización 2026-11-03 (consolidación GitHub + SDD)

La documentación operativa de plataforma para Spec-Driven Development está en
[`docs/plataforma/00_indice.md`](plataforma/00_indice.md).

`main` en GitHub (`antonioavezon/ESP-DataScience`) contiene HUC consolidado;
el laboratorio previo está en `archive/esp-datascience-lab/`.
