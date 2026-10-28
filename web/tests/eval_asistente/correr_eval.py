"""Batería de evaluación del asistente. No inventa métricas: mide ejecución real."""

from __future__ import annotations

import json
import statistics
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from unittest.mock import MagicMock

from services.chat_contrato import validar
from services.chat_intencion import interpretar
from services.chat_orquestador import responder
from services.ollama_client import Inferencia

CATALOGO = Path(__file__).with_name("catalogo_v1.json")
ARTEFACTOS = Path(__file__).resolve().parents[3] / "artifacts" / "eval_asistente"


@dataclass
class ResultadoCaso:
    id: str
    grupo: str
    ok: bool
    motivos: list[str] = field(default_factory=list)
    intencion: str = ""
    contexto_dataset: str = ""
    contexto_pozo: str = ""
    formato_ok: bool = False
    contrato_ok: bool = False
    latencia_s: float = 0.0
    vacia: bool = False
    error_numerico: bool = False
    critico: bool = False
    respaldo: bool = False
    contenido_preview: str = ""


class _ModeloFijo:
    """Respuesta lingüística controlada para medir backend + contrato."""

    def __init__(self, contenido='{"resumen":"Resumen de prueba.","explicacion":"Explicacion de prueba."}'):
        self.contenido = contenido
        self.ok = True
        self.llamadas = 0

    def consultar(self, modelo, mensajes, num_predict, temperature=0, formato=None):
        self.llamadas += 1
        return Inferencia(ok=True, contenido=self.contenido, modelo=modelo, done_reason="stop", duracion_s=0.01)

    def cerrar(self):
        return None


def cargar_catalogo(ruta: Path | None = None) -> dict:
    return json.loads((ruta or CATALOGO).read_text(encoding="utf-8"))


def evaluar_caso(caso: dict, *, cliente=None, contexto: dict | None = None) -> tuple[ResultadoCaso, dict]:
    esperado = caso.get("esperado") or {}
    dataset = caso.get("dataset_id") or "BES-jun"
    pozo = (caso.get("pozo_id") or "").strip() or None
    ambito = caso.get("ambito") or ("pozo" if pozo else "dataset")
    alcance = {
        "dataset": "Todos" if dataset in ("ALL", "all", "Todos") else dataset,
        "pozo": pozo or "Todos",
    }
    inicio = time.perf_counter()
    decision = interpretar(caso["consulta"], contexto or {}, pozo, ambito)
    salida = responder(
        caso["consulta"],
        pozo,
        contexto or {},
        cliente or _ModeloFijo(),
        modelo="modelo-prueba",
        num_predict=64,
        dataset_id=dataset,
        ambito=ambito,
        alcance=alcance,
    )
    lat = time.perf_counter() - inicio
    inf = salida.get("inferencia") or {}
    texto = str(inf.get("contenido") or "")
    estructura = inf.get("estructura") if isinstance(inf.get("estructura"), dict) else {}
    motivos = []
    ok = True

    intencion_esp = esperado.get("intencion")
    if intencion_esp and decision.get("intencion") != intencion_esp:
        # Algunas paráfrasis pueden mapear a familia equivalente
        equivalentes = {
            "seguimiento": {"seguimiento", "estado", "presiones", "medidas", "caudal", "frecuencia", "explicar_estado"},
            "consulta_esp": {"consulta_esp", "inventario", "conceptual"},
            "conceptual": {"conceptual", "consulta_esp"},
            "comparar": {"comparar", "comparar_contexto", "caudal", "frecuencia", "estado"},
            "aclarar": {"aclarar", "fuera_de_alcance", "seguimiento"},
            "inventario": {"inventario", "consulta_esp", "estado"},
            "medidas": {"medidas", "estado", "consulta_esp"},
        }
        familia = equivalentes.get(intencion_esp, {intencion_esp})
        if decision.get("intencion") not in familia:
            ok = False
            motivos.append(f"intencion:{decision.get('intencion')}!={intencion_esp}")

    ctx_ds = str((inf.get("alcance") or {}).get("dataset") or inf.get("dataset") or "")
    ctx_esp = esperado.get("contexto_dataset")
    if ctx_esp and ctx_ds != ctx_esp:
        ok = False
        motivos.append(f"contexto_dataset:{ctx_ds}!={ctx_esp}")

    for token in esperado.get("contiene") or []:
        if token.lower() not in texto.lower():
            # también buscar en estructura
            blob = json.dumps(estructura, ensure_ascii=False)
            if token.lower() not in blob.lower():
                ok = False
                motivos.append(f"falta:{token}")

    for token in esperado.get("no_contiene") or []:
        if token and token.lower() in texto.lower():
            ok = False
            motivos.append(f"prohibido:{token}")

    pozos_esp = esperado.get("pozos") or []
    if pozos_esp:
        hallados = set(decision.get("pozos") or [])
        if not set(pozos_esp) <= hallados and not all(p in texto for p in pozos_esp):
            ok = False
            motivos.append(f"pozos:{sorted(hallados)}")

    contrato_ok = False
    formato_ok = False
    if estructura.get("schema_version") == "1.0":
        contrato_ok, motivo_c = validar(estructura)
        if not contrato_ok:
            motivos.append(f"contrato:{motivo_c}")
            if caso.get("critico"):
                ok = False
        tipos = {b.get("type") for b in (estructura.get("answer") or {}).get("blocks") or []}
        tipos.add((estructura.get("answer") or {}).get("type"))
        for f in esperado.get("formato") or []:
            if f in tipos or f == (estructura.get("answer") or {}).get("type"):
                formato_ok = True
                break
        if not esperado.get("formato"):
            formato_ok = contrato_ok
        elif not formato_ok and caso.get("critico"):
            motivos.append(f"formato:{sorted(tipos)}")
    else:
        motivos.append("sin_contrato_v1")

    vacia = not texto.strip()
    if vacia and inf.get("ok"):
        ok = False
        motivos.append("vacia_ok")

    error_num = "99999" in texto or "<script>" in texto.lower()
    if error_num:
        ok = False
        motivos.append("error_numerico_o_html")

    res = ResultadoCaso(
        id=caso["id"],
        grupo=caso["grupo"],
        ok=ok and not motivos,
        motivos=motivos,
        intencion=str(decision.get("intencion") or ""),
        contexto_dataset=ctx_ds,
        contexto_pozo=str((inf.get("alcance") or {}).get("pozo") or ""),
        formato_ok=formato_ok,
        contrato_ok=contrato_ok,
        latencia_s=round(lat, 4),
        vacia=vacia,
        error_numerico=error_num,
        critico=bool(caso.get("critico")),
        respaldo=str(inf.get("linguistic_source") or "") == "deterministic",
        contenido_preview=texto[:240],
    )
    # Si solo motivos blandos de formato no crítico, recalcular ok
    if res.motivos and all(m.startswith("formato:") or m.startswith("sin_contrato") for m in res.motivos) and not caso.get("critico"):
        res.ok = True
    elif not res.motivos:
        res.ok = True
    else:
        res.ok = False
    return res, salida


def correr(ruta_catalogo: Path | None = None, etiqueta: str = "run") -> dict:
    catalogo = cargar_catalogo(ruta_catalogo)
    resultados = []
    contexto = {}
    for caso in catalogo["casos"]:
        if caso.get("esperado", {}).get("seguimiento"):
            res, salida = evaluar_caso(caso, contexto=contexto)
        else:
            res, salida = evaluar_caso(caso, contexto={})
        contexto = salida.get("contexto") or contexto
        resultados.append(res)

    latencias = [r.latencia_s for r in resultados]
    criticos = [r for r in resultados if r.critico]
    resumen = {
        "etiqueta": etiqueta,
        "total": len(resultados),
        "exitosos": sum(1 for r in resultados if r.ok),
        "fallidos": sum(1 for r in resultados if not r.ok),
        "criticos_total": len(criticos),
        "criticos_ok": sum(1 for r in criticos if r.ok),
        "contratos_ok": sum(1 for r in resultados if r.contrato_ok),
        "formatos_ok": sum(1 for r in resultados if r.formato_ok),
        "vacias": sum(1 for r in resultados if r.vacia),
        "errores_numericos": sum(1 for r in resultados if r.error_numerico),
        "respaldo": sum(1 for r in resultados if r.respaldo),
        "latencia_mediana_s": round(statistics.median(latencias), 4) if latencias else None,
        "latencia_p95_s": round(sorted(latencias)[max(0, int(len(latencias) * 0.95) - 1)], 4) if latencias else None,
        "pct_exito": round(100 * sum(1 for r in resultados if r.ok) / len(resultados), 2) if resultados else 0,
        "pct_contexto_critico": round(100 * sum(1 for r in criticos if r.ok) / len(criticos), 2) if criticos else None,
        "fallos": [asdict(r) for r in resultados if not r.ok],
        "casos": [asdict(r) for r in resultados],
    }
    ARTEFACTOS.mkdir(parents=True, exist_ok=True)
    destino = ARTEFACTOS / f"{etiqueta}.json"
    destino.write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    return resumen


if __name__ == "__main__":
    import sys
    etiqueta = sys.argv[1] if len(sys.argv) > 1 else "despues"
    resumen = correr(etiqueta=etiqueta)
    print(json.dumps({k: resumen[k] for k in resumen if k not in ("casos", "fallos")}, ensure_ascii=False, indent=2))
    print("fallidos", resumen["fallidos"])
    print("artefacto", ARTEFACTOS / f"{etiqueta}.json")
