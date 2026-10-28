"""Adaptador hacia el motor ya escrito. No reimplementa ecuaciones."""

from __future__ import annotations

import importlib.util
import sys
from typing import Any

from services.dataset_registry import FichaDataset

ENTRADAS_OPERACIONALES = (
    ("caudal_operacion_bfpd", "BFPD"),
    ("frecuencia_hz", "Hz"),
    ("presion_sensor_psi", "psi"),
    ("thp_psi", "psi"),
    ("api_deg", "°API"),
    ("bsw_numero", "fracción"),
    ("temperatura_c", "°C"),
)
UNIDADES = dict(ENTRADAS_OPERACIONALES)


class AdaptadorHUC:
    def __init__(self, ficha: FichaDataset):
        self.ficha = ficha

    def notas_resultado(self) -> dict[str, str]:
        return {}

    def documentos_contexto(self) -> list[dict[str, str]]:
        return []

    def evaluar(self, pozo_id: str, mediciones: dict[str, float] | None = None) -> dict[str, Any]:
        raise NotImplementedError

    def evaluar_escenario(self, pozo_id: str, variables, parametros_escenario, escenario_id: str, simular: bool) -> dict[str, Any]:
        return self.evaluar(pozo_id)


class AdaptadorSinMotor(AdaptadorHUC):
    def evaluar(self, pozo_id: str, mediciones: dict[str, float] | None = None) -> dict[str, Any]:
        return {
            "estado_evaluacion": "no_disponible",
            "dataset_solicitado": self.ficha.identificador,
            "dataset_evaluado": None,
            "pozo_solicitado": pozo_id,
            "recomendacion_operacional_autorizada": False,
            "errores": [{"codigo": "SIN_MOTOR", "mensaje": self.ficha.causa_sin_evaluacion or "No disponible"}],
            "advertencias": [],
            "mensajes": [],
            "modelos": [],
            "reglas": [],
        }


class AdaptadorBesJun(AdaptadorHUC):
    def notas_resultado(self) -> dict[str, str]:
        return {}

    def documentos_contexto(self) -> list[dict[str, str]]:
        documentos = []
        for relativo in (
            "integracion/capa_linguistica.md",
        ):
            ruta = self.ficha.ruta / relativo
            if not ruta.is_file():
                continue
            texto = ruta.read_text(encoding="utf-8")
            documentos.append({
                "fuente": str(ruta.relative_to(self.ficha.ruta.parent.parent.parent)),
                "extracto": texto[:2500],
            })
        return documentos

    def evaluar(self, pozo_id: str, mediciones: dict[str, float] | None = None) -> dict[str, Any]:
        if not self.ficha.puede_evaluar:
            return AdaptadorSinMotor(self.ficha).evaluar(pozo_id, mediciones)
        conocidos = {str(item.get("pozo_rotulo")) for item in self.ficha.pozos()}
        if pozo_id not in conocidos:
            return {
                "estado_evaluacion": "entrada_invalida",
                "dataset_solicitado": self.ficha.identificador,
                "dataset_evaluado": None,
                "pozo_solicitado": pozo_id,
                "recomendacion_operacional_autorizada": False,
                "errores": [{"codigo": "POZO_DESCONOCIDO", "mensaje": "Ese pozo no está en integracion/pozos.json."}],
                "advertencias": [],
                "mensajes": [],
                "modelos": [],
                "reglas": [],
            }
        variables = []
        for nombre, valor in (mediciones or {}).items():
            if nombre not in UNIDADES or valor is None:
                continue
            variables.append({
                "nombre": nombre,
                "valor": valor,
                "unidad": UNIDADES[nombre],
                "procedencia": "operador",
            })
        version = "1.3.0"
        if self.ficha.manifiesto and isinstance(self.ficha.manifiesto.get("esquema_contrato"), str):
            version = self.ficha.manifiesto["esquema_contrato"]
        solicitud = {
            "dataset_id": self.ficha.identificador,
            "pozo_id": pozo_id,
            "version_configuracion": version,
            "fecha_observacion": None,
            "variables": variables,
        }
        src = self.ficha.ruta / "src"
        if str(src) not in sys.path:
            sys.path.insert(0, str(src))
        from evaluacion.motor import evaluar_solicitud

        return evaluar_solicitud(solicitud)

    def evaluar_escenario(
        self,
        pozo_id: str,
        variables: list[dict],
        parametros_escenario: dict,
        escenario_id: str,
        simular: bool,
    ) -> dict[str, Any]:
        if not self.ficha.puede_evaluar:
            return AdaptadorSinMotor(self.ficha).evaluar(pozo_id)
        version = "1.3.0"
        if self.ficha.manifiesto and isinstance(self.ficha.manifiesto.get("esquema_contrato"), str):
            version = self.ficha.manifiesto["esquema_contrato"]
        solicitud = {
            "dataset_id": self.ficha.identificador,
            "pozo_id": pozo_id,
            "version_configuracion": version,
            "fecha_observacion": None,
            "variables": variables,
        }
        if simular:
            solicitud["modo"] = "simulacion"
            solicitud["escenario_id"] = escenario_id
            solicitud["parametros_escenario"] = parametros_escenario
        src = self.ficha.ruta / "src"
        if str(src) not in sys.path:
            sys.path.insert(0, str(src))
        from evaluacion.motor import evaluar_solicitud

        return evaluar_solicitud(solicitud)


class AdaptadorExpediente(AdaptadorHUC):
    """Carga el motor del expediente por archivo, sin pisar el módulo de otro dataset."""

    def evaluar_escenario(self, pozo_id, variables, parametros_escenario, escenario_id, simular):
        if not self.ficha.puede_evaluar:
            return AdaptadorSinMotor(self.ficha).evaluar(pozo_id)
        solicitud = {
            "dataset_id": self.ficha.identificador,
            "pozo_id": pozo_id,
            "variables": variables,
            "modo": "simulacion" if simular else "escenario_inicial",
            "escenario_id": escenario_id,
        }
        return self._motor().evaluar_solicitud(solicitud)

    def evaluar(self, pozo_id, mediciones=None):
        return self.evaluar_escenario(pozo_id, [], {}, "", False)

    def _motor(self):
        ruta = self.ficha.ruta / "src" / "evaluacion" / "motor.py"
        nombre = "huc_expediente_" + self.ficha.identificador.replace("-", "_")
        cargado = sys.modules.get(nombre)
        if cargado is not None and getattr(cargado, "__file__", None) == str(ruta):
            return cargado
        src = str(self.ficha.ruta / "src")
        if src not in sys.path:
            sys.path.insert(0, src)
        spec = importlib.util.spec_from_file_location(nombre, ruta)
        modulo = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = modulo
        spec.loader.exec_module(modulo)
        return modulo


def adaptador_para(ficha: FichaDataset) -> AdaptadorHUC:
    if ficha.puede_evaluar and ficha.identificador == "BES-jun":
        return AdaptadorBesJun(ficha)
    if ficha.puede_evaluar and (ficha.ruta / "src" / "evaluacion" / "motor.py").is_file():
        return AdaptadorExpediente(ficha)
    return AdaptadorSinMotor(ficha)


def medicion_o_ausente(texto: str) -> float | None:
    """Un campo en blanco no es cero. Un texto no numérico se rechaza afuera."""
    if texto is None or str(texto).strip() == "":
        return None
    return float(str(texto).strip().replace(",", "."))
