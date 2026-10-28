"""Cliente HTTP de Ollama. Una respuesta 200 no basta para darla por buena."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field

import httpx

ENTRADA_MAXIMA = 4000
PREDICT_MAXIMO = 1024
TIMEOUT_MAXIMO = 120


def configuracion() -> dict:
    timeout = _acotar(os.environ.get("OLLAMA_TIMEOUT_S", "60"), 5, TIMEOUT_MAXIMO, 60)
    predict = _acotar(os.environ.get("OLLAMA_NUM_PREDICT", "512"), 32, PREDICT_MAXIMO, 512)
    return {
        "base_url": os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/"),
        "modelo": os.environ.get("OLLAMA_MODEL", "qwen3:4b-instruct-2507-q4_K_M"),
        "timeout_s": timeout,
        "num_predict": int(predict),
    }


def _acotar(texto: str, minimo: float, maximo: float, defecto: float) -> float:
    try:
        valor = float(texto)
    except (TypeError, ValueError):
        return defecto
    return min(maximo, max(minimo, valor))


@dataclass
class Inferencia:
    ok: bool
    contenido: str = ""
    error: str = ""
    incompleta: bool = False
    modelo: str = ""
    done_reason: str = ""
    duracion_s: float | None = None
    tokens_generados: int | None = None
    thinking_descartado: bool = False
    modelos: list[dict] = field(default_factory=list)

    def a_dict(self) -> dict:
        return {
            "ok": self.ok,
            "contenido": self.contenido,
            "error": self.error,
            "incompleta": self.incompleta,
            "modelo": self.modelo,
            "done_reason": self.done_reason,
            "duracion_s": self.duracion_s,
            "tokens_generados": self.tokens_generados,
            "thinking_descartado": self.thinking_descartado,
        }


class ClienteOllama:
    def __init__(self, base_url: str, timeout_s: float, cliente: httpx.Client | None = None):
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self._cliente = cliente
        self._propio = cliente is None

    def cerrar(self) -> None:
        if self._propio and self._cliente is not None:
            self._cliente.close()

    def _http(self) -> httpx.Client:
        if self._cliente is None:
            self._cliente = httpx.Client(timeout=self.timeout_s, trust_env=False)
        return self._cliente

    def modelos(self) -> Inferencia:
        try:
            respuesta = self._http().get(f"{self.base_url}/api/tags")
            respuesta.raise_for_status()
            documento = respuesta.json()
        except httpx.TimeoutException:
            return Inferencia(ok=False, error="Tiempo de espera agotado al consultar Ollama.")
        except httpx.HTTPError as exc:
            return Inferencia(ok=False, error=f"Ollama no está disponible: {exc.__class__.__name__}.")
        except ValueError:
            return Inferencia(ok=False, error="Ollama devolvió un JSON inválido al listar modelos.")
        crudos = documento.get("models") if isinstance(documento, dict) else None
        if not isinstance(crudos, list):
            return Inferencia(ok=False, error="La lista de modelos no tiene el formato esperado.")
        lista = []
        for item in crudos:
            if not isinstance(item, dict) or not item.get("name"):
                continue
            capacidades = (item.get("details") or {}).get("capabilities") or item.get("capabilities") or []
            if not isinstance(capacidades, list):
                capacidades = []
            lista.append({
                "nombre": item["name"],
                "thinking": "thinking" in capacidades,
            })
        return Inferencia(ok=True, modelos=lista)

    def consultar(
        self,
        modelo: str,
        mensajes: list[dict],
        num_predict: int,
        *,
        temperature: float = 0,
        formato: str | dict | None = None,
    ) -> Inferencia:
        if not modelo or not str(modelo).strip():
            return Inferencia(ok=False, error="No hay un modelo seleccionado.")
        inventario = self.modelos()
        if not inventario.ok:
            return inventario
        nombres = {item["nombre"] for item in inventario.modelos}
        if modelo not in nombres:
            return Inferencia(
                ok=False,
                error=f"El modelo {modelo} no está instalado. No se eligió otro en su lugar.",
                modelo=modelo,
                modelos=inventario.modelos,
            )
        cuerpo = {
            "model": modelo,
            "messages": mensajes,
            "stream": False,
            "think": False,
            "options": {
                "temperature": float(min(1.0, max(0.0, temperature))),
                "num_predict": int(min(PREDICT_MAXIMO, max(1, num_predict))),
            },
        }
        if formato is not None:
            cuerpo["format"] = formato
        inicio = time.perf_counter()
        try:
            respuesta = self._http().post(f"{self.base_url}/api/chat", json=cuerpo)
            respuesta.raise_for_status()
            documento = respuesta.json()
        except httpx.TimeoutException:
            return Inferencia(ok=False, modelo=modelo, error="Tiempo de espera agotado durante la inferencia.")
        except httpx.HTTPError as exc:
            return Inferencia(ok=False, modelo=modelo, error=f"Error HTTP al consultar el modelo: {exc.__class__.__name__}.")
        except ValueError:
            return Inferencia(ok=False, modelo=modelo, error="Ollama devolvió un JSON inválido en la inferencia.")
        duracion = time.perf_counter() - inicio
        if not isinstance(documento, dict):
            return Inferencia(ok=False, modelo=modelo, error="La inferencia no devolvió un objeto JSON.", duracion_s=duracion)
        mensaje = documento.get("message") if isinstance(documento.get("message"), dict) else {}
        thinking = mensaje.get("thinking") or ""
        contenido = mensaje.get("content") or ""
        if not isinstance(contenido, str):
            contenido = ""
        if not isinstance(thinking, str):
            thinking = ""
        razon = str(documento.get("done_reason") or "")
        tokens = documento.get("eval_count")
        tokens_n = tokens if isinstance(tokens, int) else None
        descartado = bool(thinking.strip())
        if not contenido.strip():
            return Inferencia(
                ok=False,
                modelo=modelo,
                error="La respuesta final está vacía. No se muestra el razonamiento interno.",
                done_reason=razon,
                duracion_s=duracion,
                tokens_generados=tokens_n,
                thinking_descartado=descartado,
                incompleta=razon == "length",
            )
        return Inferencia(
            ok=True,
            contenido=contenido.strip(),
            modelo=modelo,
            done_reason=razon,
            duracion_s=duracion,
            tokens_generados=tokens_n,
            thinking_descartado=descartado,
            incompleta=razon == "length",
        )
