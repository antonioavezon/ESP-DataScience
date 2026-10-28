# Comparación RB-IA-2191 frente a BES-jun y RB-1521

Fecha: 2026-10-28. No altera fórmulas de otros expedientes.

| Dimensión | BES-jun | RB-1521 | RB-IA-2191 |
|---|---|---|---|
| Formato | xlsx multi-hoja | xls serie diaria | xlsx serie diaria |
| Pozos | 5 (QF-*) | 1 (RB-1521) | 1 (RB-IA-2191) |
| Motor | fluido + balance + intersección + RC-BES | Q-water = Q×BSW | BOPD = BFPD−BWPD |
| Regla de caudal | RC-BES candidatas | ninguna | ninguna |
| Rótulo típico | NORMAL/… | REGISTRO | REGISTRO |
| Controles | frecuencia, caudal operación | caudal_fluidos, bsw | bfpd, bwpd |
| Notebooks | 12 (algunos pares históricos) | 6 + PDF | 6 + PDF |
| Pruebas | 182 | 6 | 6 |
| Ciclo | en_uso | en_uso | en_uso |
| procesadas | no | no | no |

Reutilización: solo infraestructura HUC (adaptador, contratos, REGISTRO). No se compartió código de partición entre RB-1521 y RB-IA-2191: BSW×BFPD no cierra en D2.
