"""Regresión: cerrar sesión debe devolver a la hoja los pozos que estaban simulados.

Antes, cerrar_sesion vaciaba los valores en uso pero no publicaba el escenario base,
y la consola seguía mostrando el último resultado simulado.
"""

import os
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
INTERFACES = RAIZ / "data" / "interfaces"
for ruta in (RAIZ, INTERFACES):
    if str(ruta) not in sys.path:
        sys.path.insert(0, str(ruta))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ["HUC_SIM_USUARIO"] = "operador"
os.environ["HUC_SIM_CLAVE"] = "clave-de-prueba"

import django  # noqa: E402

django.setup()

from django.test import Client, override_settings  # noqa: E402

from data.simuladores import valores_en_uso as vu  # noqa: E402
from simulador import views  # noqa: E402


@pytest.fixture
def publicados(monkeypatch):
    enviados: list[dict] = []

    def falso_publicar(documento):
        enviados.append(documento)
        return None

    monkeypatch.setattr(views, "publicar", falso_publicar)
    vu.limpiar_todo()
    yield enviados
    vu.limpiar_todo()


@override_settings(
    SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies",
    HUC_SIM_USUARIO="operador",
    HUC_SIM_CLAVE="clave-de-prueba",
    ALLOWED_HOSTS=["testserver"],
)
def test_cerrar_sesion_republica_base_de_pozos_simulados(publicados):
    cliente = Client()
    r = cliente.post("/api/acceder/", {"usuario": "operador", "clave": "clave-de-prueba"}, content_type="application/json")
    assert r.status_code == 200

    r = cliente.post("/api/pozos/QF-084/aplicar/", {"valores": {"frecuencia_hz": 60}}, content_type="application/json")
    assert r.status_code == 200
    assert vu.activos() == ["QF-084"]
    assert publicados[-1]["modo"] == "simulacion"

    publicados.clear()
    r = cliente.post("/api/cerrar-sesion/")
    assert r.status_code == 200
    assert r.json()["restaurados"] == ["QF-084"]
    assert vu.activos() == []
    # Se publicó exactamente un escenario base, sin controles modificados, para el pozo simulado.
    assert len(publicados) == 1
    base = publicados[0]
    assert base["pozo_id"] == "QF-084"
    assert base["controles"] == {}
    assert base["modo"] == "escenario_inicial"


@override_settings(
    SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies",
    HUC_SIM_USUARIO="operador",
    HUC_SIM_CLAVE="clave-de-prueba",
    ALLOWED_HOSTS=["testserver"],
)
def test_cerrar_sesion_sin_simulacion_no_publica(publicados):
    cliente = Client()
    cliente.post("/api/acceder/", {"usuario": "operador", "clave": "clave-de-prueba"}, content_type="application/json")
    r = cliente.post("/api/cerrar-sesion/")
    assert r.status_code == 200
    assert r.json()["restaurados"] == []
    assert publicados == []
