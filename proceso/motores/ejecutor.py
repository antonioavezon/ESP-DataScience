"""Ejecuta el motor ya existente. No reescribe fórmulas."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
WEB = RAIZ / "web"
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
if str(WEB) not in sys.path:
    sys.path.insert(0, str(WEB))


def evaluar(pozo_id: str, controles: dict | None = None, escenario_id: str = "", evaluacion_id: str = "", explicar: bool = False) -> tuple[int, dict]:
    from services.consola_operacional import evaluar_pozo

    return evaluar_pozo(pozo_id, controles or {}, escenario_id, evaluacion_id, explicar)


def publicar_linea_base() -> list[dict]:
    """Calcula el punto escrito en cada hoja. No modifica el Excel."""
    from services.escenario_inicial import listar_pozos

    publicados = []
    for pozo in listar_pozos():
        if not pozo.get("evaluable"):
            continue
        try:
            codigo, cuerpo = evaluar(pozo["pozo_id"], {}, "", f"base-{pozo['pozo_id']}", False)
        except Exception as exc:
            publicados.append({
                "codigo_http": 500,
                "cuerpo": {"pozo_id": pozo["pozo_id"], "ok": False, "error": exc.__class__.__name__},
            })
            continue
        publicados.append({"codigo_http": codigo, "cuerpo": cuerpo})
    return publicados
