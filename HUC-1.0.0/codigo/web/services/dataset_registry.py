"""Registro de expedientes. No abre libros ni promueve carpetas."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

CICLO = ("en_espera", "en_uso", "procesadas")
IDENTIFICADOR = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,64}$")


def raiz_huc() -> Path:
    return Path(__file__).resolve().parents[2]


@dataclass
class FichaDataset:
    identificador: str
    ciclo: str
    ruta: Path
    descripcion: str
    estado_declarado: str
    modificado: datetime | None
    manifiesto: dict | None = None
    archivos: dict[str, bool] = field(default_factory=dict)
    limitaciones: list[str] = field(default_factory=list)
    causa_sin_evaluacion: str = ""

    @property
    def puede_evaluar(self) -> bool:
        return not self.causa_sin_evaluacion

    def a_dict(self) -> dict:
        return {
            "identificador": self.identificador,
            "ciclo": self.ciclo,
            "descripcion": self.descripcion,
            "estado_declarado": self.estado_declarado,
            "modificado": self.modificado.isoformat() if self.modificado else None,
            "archivos": dict(self.archivos),
            "limitaciones": list(self.limitaciones),
            "puede_evaluar": self.puede_evaluar,
            "causa_sin_evaluacion": self.causa_sin_evaluacion,
            "pozos": self.pozos(),
        }

    def leer_json(self, relativo: str):
        ruta = self.ruta / relativo
        if not ruta.is_file():
            return None
        return json.loads(ruta.read_text(encoding="utf-8"))

    def pozos(self) -> list[dict]:
        documento = self.leer_json("integracion/pozos.json")
        if not isinstance(documento, dict):
            return []
        pozos = documento.get("pozos")
        if not isinstance(pozos, list):
            return []
        return [item for item in pozos if isinstance(item, dict)]

    def variables(self) -> list[dict]:
        documento = self.leer_json("integracion/variables.json")
        if not isinstance(documento, dict) or not isinstance(documento.get("variables"), list):
            return []
        return documento["variables"]

    def reglas(self) -> list[dict]:
        documento = self.leer_json("integracion/reglas.json")
        if not isinstance(documento, dict) or not isinstance(documento.get("reglas"), list):
            return []
        return documento["reglas"]

    def resultados_csv(self) -> list[dict]:
        ruta = self.ruta / "data_procesados" / "resultados_deterministicos.csv"
        if not ruta.is_file():
            return []
        import csv

        with ruta.open(encoding="utf-8", newline="") as archivo:
            return list(csv.DictReader(archivo))


def descubrir(base: Path | None = None) -> list[FichaDataset]:
    raiz = base or raiz_huc()
    encontrados: list[FichaDataset] = []
    for ciclo in CICLO:
        carpeta = raiz / "datasets" / ciclo
        if not carpeta.is_dir():
            continue
        for ruta in sorted(item for item in carpeta.iterdir() if item.is_dir()):
            ficha = _ficha(ruta, ciclo)
            if ficha is not None:
                encontrados.append(ficha)
    return encontrados


def obtener(identificador: str, base: Path | None = None) -> FichaDataset | None:
    if not IDENTIFICADOR.fullmatch(identificador or ""):
        return None
    for ficha in descubrir(base):
        if ficha.identificador == identificador:
            return ficha
    return None


def _ficha(ruta: Path, ciclo: str) -> FichaDataset | None:
    ficha_md = ruta / "dataset.md"
    if not ficha_md.is_file() and not (ruta / "integracion" / "manifiesto.json").is_file():
        return None
    texto = ficha_md.read_text(encoding="utf-8") if ficha_md.is_file() else ""
    manifiesto = None
    ruta_manifiesto = ruta / "integracion" / "manifiesto.json"
    if ruta_manifiesto.is_file():
        manifiesto = json.loads(ruta_manifiesto.read_text(encoding="utf-8"))
    identificador = ruta.name
    if isinstance(manifiesto, dict) and isinstance(manifiesto.get("dataset_id"), str):
        identificador = manifiesto["dataset_id"]
    else:
        declarado = _campo(texto, "Identificador")
        if declarado:
            identificador = declarado.strip("`")
    if not IDENTIFICADOR.fullmatch(identificador):
        return None
    modificado = datetime.fromtimestamp(ficha_md.stat().st_mtime, timezone.utc) if ficha_md.is_file() else None
    archivos = {
        "ficha": ficha_md.is_file(),
        "entrada": _entrada_presente(ruta, manifiesto),
        "resultados": (ruta / "data_procesados" / "resultados_deterministicos.csv").is_file(),
        "contrato_entrada": (ruta / "integracion" / "contrato_entrada.schema.json").is_file(),
        "contrato_salida": (ruta / "integracion" / "contrato_salida.schema.json").is_file(),
        "manifiesto": ruta_manifiesto.is_file(),
        "pozos": (ruta / "integracion" / "pozos.json").is_file(),
        "variables": (ruta / "integracion" / "variables.json").is_file(),
        "reglas": (ruta / "integracion" / "reglas.json").is_file(),
        "motor": (ruta / "src" / "evaluacion" / "motor.py").is_file(),
    }
    limitaciones = []
    if isinstance(manifiesto, dict) and isinstance(manifiesto.get("limitaciones"), list):
        limitaciones = [str(item) for item in manifiesto["limitaciones"]]
    causa = ""
    if not (archivos["motor"] and archivos["contrato_entrada"] and archivos["contrato_salida"] and archivos["manifiesto"]):
        if ciclo == "en_espera":
            causa = "El expediente está en espera. No hay paquete de integración ni motor, y esta aplicación no abre el archivo original."
        elif ciclo == "procesadas":
            causa = "No hay un paquete de integración utilizable en esta carpeta."
        else:
            causa = "Faltan el motor o los contratos de integración. La evaluación queda deshabilitada."
    return FichaDataset(
        identificador=identificador,
        ciclo=ciclo,
        ruta=ruta,
        descripcion=_descripcion(texto),
        estado_declarado=_campo(texto, "Estado") or (str(manifiesto.get("estado_dataset")) if isinstance(manifiesto, dict) else "No disponible"),
        modificado=modificado,
        manifiesto=manifiesto if isinstance(manifiesto, dict) else None,
        archivos=archivos,
        limitaciones=limitaciones,
        causa_sin_evaluacion=causa,
    )


def _entrada_presente(ruta: Path, manifiesto) -> bool:
    if not isinstance(manifiesto, dict):
        return False
    relativo = manifiesto.get("archivo_entrada")
    if not isinstance(relativo, str) or not relativo or relativo.startswith(("/", "\\")) or ".." in Path(relativo).parts:
        return False
    return (ruta / relativo).is_file()


def _campo(texto: str, nombre: str) -> str:
    prefijo = f"**{nombre}:**"
    for linea in texto.splitlines():
        if linea.startswith(prefijo):
            return linea[len(prefijo):].strip().strip("`")
    return ""


def _descripcion(texto: str) -> str:
    lineas = []
    for linea in texto.splitlines():
        limpia = linea.strip()
        if not limpia or limpia.startswith("#") or limpia.startswith("|") or limpia.startswith("**"):
            if lineas and limpia.startswith("#"):
                break
            continue
        lineas.append(limpia)
        if len(" ".join(lineas)) > 700:
            break
    resumen = " ".join(lineas)
    return resumen[:1200] if resumen else "No disponible"
