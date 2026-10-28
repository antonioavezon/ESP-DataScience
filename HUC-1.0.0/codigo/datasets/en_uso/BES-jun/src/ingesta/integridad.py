"""Control de identidad binaria de archivos.

Qué prueba: que dos archivos tienen exactamente los mismos bytes.
Qué no prueba: que el contenido sea correcto, completo ni apto para decidir.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def huellas_de_bytes(contenido: bytes) -> dict:
    return {
        "bytes": len(contenido),
        "sha256": hashlib.sha256(contenido).hexdigest(),
        "md5": hashlib.md5(contenido).hexdigest(),
    }


def huellas(ruta: Path) -> dict:
    """Tamaño, SHA-256 y MD5 de un archivo, leído en bloques y sin modificarlo."""
    sha, md5, n = hashlib.sha256(), hashlib.md5(), 0
    with Path(ruta).open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(bloque)
            md5.update(bloque)
            n += len(bloque)
    return {"bytes": n, "sha256": sha.hexdigest(), "md5": md5.hexdigest()}


def comparar(rutas: dict[str, Path]) -> dict:
    """Huella de cada ruta y veredicto de coincidencia.

    Si una ruta no existe se informa como ausente y el veredicto es False:
    un control que no puede ejecutarse no se considera aprobado.
    """
    filas, ausentes = [], []
    for nombre, ruta in rutas.items():
        ruta = Path(ruta)
        if not ruta.is_file():
            ausentes.append(nombre)
            filas.append({"copia": nombre, "ruta": str(ruta), "presente": False})
            continue
        filas.append({"copia": nombre, "ruta": str(ruta), "presente": True, **huellas(ruta)})
    presentes = [f for f in filas if f["presente"]]
    coincide = (
        not ausentes
        and len(presentes) >= 2
        and len({f["sha256"] for f in presentes}) == 1
        and len({f["md5"] for f in presentes}) == 1
        and len({f["bytes"] for f in presentes}) == 1
    )
    return {"filas": filas, "ausentes": ausentes, "coincide": coincide}


def control_negativo(ruta: Path) -> dict:
    """Prueba de sensibilidad: cambia un bit en memoria y verifica que la huella cambie.

    No escribe nada en disco. Demuestra que la comparación es capaz de fallar.
    """
    original = Path(ruta).read_bytes()
    alterado = bytearray(original)
    posicion = len(alterado) // 2
    alterado[posicion] ^= 0x01
    h0, h1 = huellas_de_bytes(original), huellas_de_bytes(bytes(alterado))
    return {
        "posicion_alterada": posicion,
        "sha256_original": h0["sha256"],
        "sha256_alterado": h1["sha256"],
        "md5_original": h0["md5"],
        "md5_alterado": h1["md5"],
        "detecta_el_cambio": h0["sha256"] != h1["sha256"] and h0["md5"] != h1["md5"],
    }
