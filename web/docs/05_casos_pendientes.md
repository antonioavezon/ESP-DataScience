# Casos pendientes

La aplicación ya lista estos expedientes. No los procesa.

## RB-1521

- Ciclo: `datasets/en_espera/RB-1521`.
- La ficha `dataset.md` dice que no hay copia de trabajo y que el libro no se abre en esta etapa.
- No hay `integracion/` ni CSV. La interfaz muestra «No disponible» en pozos, resultados, reglas y variables.
- La evaluación está deshabilitada. La causa visible es que el expediente está en espera y esta aplicación no abre el original.
- Sigue siendo D1 en el tablero de asesor-esp. P-14 no se responde desde aquí.

## RB-IA-2191

Igual que el anterior, en `datasets/en_espera/RB-IA-2191`, como D2. No se leyó `RB-IA-2191-Data.xlsx`.

## BES-jun, lo que la web no cierra

- Ninguna regla está aprobada. RC-BES-04 sigue no evaluable.
- CT-03: el PIP mostrado es el de la celda. La nota de la ficha dice que el signo frente a la hidrostática no está confirmado.
- El rótulo `psi*ft` del gradiente no se reescribe.
- No hay series graficadas. No se añadieron curvas de demostración.
- No hay catálogo de pozos que mezcle datasets.
- No se mueve el expediente a `procesadas`.

## Para incorporar otro dataset

1. Dejarlo en `en_espera`, `en_uso` o `procesadas` con `dataset.md`. Aparece solo.
2. Cuando exista un paquete `integracion/` y un motor propio, añadir una clase en `services/huc_adapter.py` y registrarla en `adaptador_para`.
3. No ramificar las plantillas con el nombre del dataset.
