# Catálogo de variables · BES-jun

Generado desde `catalogo.variables_bes_jun`. El rango observado no es un límite de operación.
Los límites de frecuencia autorizados no están en el libro y no se inventan.

| Nombre | Función | Unidad canónica | Obligatoria | Estado | Rango observado |
|---|---|---|---|---|---|
| `hoja` | identificacion | — | sí | provisional | — |
| `cluster` | identificacion | — | sí | pendiente | — |
| `pozo` | identificacion | — | sí | pendiente | — |
| `bomba_referencia` | caracteristica_de_bomba | — | sí | pendiente | — |
| `etapas` | caracteristica_de_bomba | 1 | sí | pendiente | 31 … 53 (n=5) |
| `id_tubing_in` | parametro_fijo_de_instalacion | in | sí | pendiente | 2.996 … 2.996 (n=5) |
| `tvd_descarga_ft` | parametro_fijo_de_instalacion | ft | sí | pendiente | 2527.36 … 2763.64 (n=5) |
| `tvd_intake_ft` | parametro_fijo_de_instalacion | ft | sí | pendiente | 2534.6 … 2769.66 (n=5) |
| `tvd_sensor_ft` | parametro_fijo_de_instalacion | ft | sí | pendiente | 2553.92 … 2790.28 (n=5) |
| `frecuencia_hz` | medicion_ingresada | Hz | sí | pendiente | 56 … 67 (n=5) |
| `caudal_operacion_bfpd` | medicion_ingresada | BFPD | sí | pendiente | 5419 … 10301 (n=5) |
| `presion_sensor_psi` | medicion_de_sensor | psi | sí | pendiente | 607 … 821 (n=5) |
| `thp_psi` | medicion_ingresada | psi | sí | pendiente | 145 … 210 (n=5) |
| `api_deg` | parametro_incierto | °API | sí | pendiente | 12 … 12 (n=5) |
| `bsw_numero` | parametro_incierto | fracción | sí | pendiente | 0.9557 … 0.9766 (n=5) |
| `temperatura_c` | parametro_incierto | °C | sí | pendiente | 62.2222 … 65.5556 (n=5) |
| `densidad_agua_lb_gal` | parametro_incierto | lb/gal | sí | pendiente | 8.345 … 8.345 (n=5) |
| `frecuencia_curva_hz` | referencia_tecnica | Hz | sí | pendiente | 60 … 60 (n=5) |
| `limite_minimo_bfpd` | limite_operacional_no_aprobado | BFPD | sí | pendiente | 2000 … 2500 (n=5) |
| `limite_maximo_bfpd` | limite_operacional_no_aprobado | BFPD | sí | pendiente | 8000 … 10000 (n=5) |
| `cono_eficiencia_bfpd` | referencia_tecnica | BFPD | no | no_evaluable | 6000 … 8000 (n=5) |
| `curva` | caracteristica_de_bomba | BFPD, ft, hp, número | sí | pendiente | — |
| `gradiente_psi_ft` | resultado_del_modelo | psi/ft | no | pendiente | — |
| `pip_ft` | resultado_del_modelo | ft | no | pendiente | — |
| `thd_total_ft` | resultado_del_modelo | ft | no | pendiente | — |
| `caudal_a_producir_bfpd` | resultado_del_modelo | BFPD | no | pendiente | — |
| `fecha_medicion` | variable_no_disponible | — | no | no_disponible | — |
| `limite_frecuencia_autorizado_hz` | variable_no_disponible | Hz | no | no_disponible | — |

La aplicación no debe pedir de nuevo un valor que ya está en `integracion/pozos.json` y que el operador no está corrigiendo. Si lo corrige, la solicitud lo declara en `variables` con su unidad.
