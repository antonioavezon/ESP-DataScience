# 13 — Propuesta de protección de `main` (pendiente de autorización)

## Estado
**No aplicada.** Requiere permisos de administración en GitHub y, en la práctica, `gh auth login` o configuración manual en la UI. El plan Free/Team/Enterprise condiciona qué reglasets están disponibles en repos privados.

## Controles propuestos (mínimos útiles)

| Control | Valor propuesto | Motivo |
|---|---|---|
| Require a pull request before merging | Sí | Trazabilidad SDD |
| Required status checks | `CI HUC` jobs + `Seguridad HUC` jobs (nombres exactos tras primera ejecución) | No merge con fallos |
| Require branches to be up to date | Opcional (puede ralentizar) | Evitar merges obsoletos |
| Restrict force pushes | Sí en `main` | Integridad |
| Restrict deletions | Sí | |
| Required approving reviews | 0 o 1 (solo propietario: 0 aceptable al inicio) | No bloquear trabajo unipersonal |
| Dismiss stale reviews | No obligatorio al inicio | |

## Consecuencias si se activa
- No se podrá hacer `git push` directo a `main` (habrá que usar PR).
- Un check fallido bloqueará el botón de merge.
- Recuperación: el propietario puede ajustar temporalmente las reglas en Settings → Branches / Rules.

## Procedimiento de recuperación
1. Settings → Rules / Branch protection → editar ruleset.
2. Desactivar temporalmente “required checks” si un falso positivo bloquea un hotfix.
3. Documentar el incidente en ADR o registro de `analisis.md` si afecta operación.

## Cómo aplicar (cuando autorice)
Opción A — UI GitHub: Settings → Rules → New ruleset → Branch targeting `main`.
Opción B — API/`gh`:
```bash
gh api repos/antonioavezon/ESP-DataScience/rulesets -f ...
```
(Exact payload se generará tras listar los nombres reales de checks de la primera ejecución verde.)

## Limitaciones conocidas
- Repos privados en plan Free pueden tener restricciones en branch protection clásica; rulesets repository rules varían por plan.
- Sin `gh` autenticado no se puede verificar ni aplicar desde esta estación.
