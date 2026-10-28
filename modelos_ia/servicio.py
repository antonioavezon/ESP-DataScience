"""Explicaciones a partir de un resultado ya calculado. No ejecuta fórmulas."""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
WEB = RAIZ / "web"
for ruta in (RAIZ, WEB):
    if str(ruta) not in sys.path:
        sys.path.insert(0, str(ruta))

from services.mensajes_operador import explicar
from services.ollama_client import configuracion

HOST = os.environ.get("HUC_IA_BIND", "127.0.0.1")
PUERTO = int(os.environ.get("HUC_IA_PORT", "8002"))


def explicar_resultado(documento: dict) -> dict:
    if not isinstance(documento, dict):
        return _respaldo({}, "El resultado no es un objeto.")
    estado = documento.get("estado") if isinstance(documento.get("estado"), dict) else {}
    texto = documento.get("texto") if isinstance(documento.get("texto"), dict) else {"mensaje": "", "accion": "", "origen": "deterministico"}
    try:
        valores = {}
        if isinstance(documento.get("entradas"), dict):
            valores.update(documento["entradas"])
        if isinstance(documento.get("resultados"), dict):
            valores.update(documento["resultados"])
        salida = explicar(estado, texto, documento.get("modificadas") or [], valores)
    except Exception:
        salida = {**texto, "origen": "deterministico", "modelo_usado": False}
    cfg = configuracion()
    generado = salida.get("origen") == "ollama" and salida.get("modelo_usado") is True
    return {
        "explicacion": salida.get("mensaje") or "",
        "accion": salida.get("accion") or "",
        "evaluacion_id": documento.get("evaluacion_id"),
        "pozo_id": documento.get("pozo_id"),
        "modelo": cfg["modelo"] if generado else "",
        "estado_generacion": "generada" if generado else "respaldo",
        "advertencias": [] if generado else ["La explicación lingüística no está disponible."],
    }


def _respaldo(documento: dict, mensaje: str) -> dict:
    return {
        "explicacion": mensaje,
        "accion": "",
        "evaluacion_id": documento.get("evaluacion_id"),
        "pozo_id": documento.get("pozo_id"),
        "modelo": "",
        "estado_generacion": "respaldo",
        "advertencias": ["La explicación lingüística no está disponible."],
    }


class Manejador(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/salud":
            self.send_error(404)
            return
        self._json(200, {"disponible": True})

    def do_POST(self):
        if self.path != "/v1/explicar":
            self.send_error(404)
            return
        longitud = int(self.headers.get("Content-Length") or "0")
        if longitud > 200_000:
            self.send_error(413)
            return
        try:
            documento = json.loads(self.rfile.read(longitud).decode("utf-8") or "{}")
        except (UnicodeDecodeError, json.JSONDecodeError):
            cuerpo = _respaldo({}, "El cuerpo no es JSON.")
            self._json(400, cuerpo)
            return
        self._json(200, explicar_resultado(documento))

    def _json(self, codigo: int, cuerpo: dict) -> None:
        carga = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(carga)))
        self.end_headers()
        self.wfile.write(carga)

    def log_message(self, formato, *args):
        return


def main() -> None:
    servidor = ThreadingHTTPServer((HOST, PUERTO), Manejador)
    servidor.serve_forever()


if __name__ == "__main__":
    main()
