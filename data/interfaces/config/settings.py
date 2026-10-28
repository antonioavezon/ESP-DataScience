import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAIZ = BASE_DIR.parents[1]

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or "clave-solo-desarrollo-local-huc-data"
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origen.strip()
    for origen in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origen.strip()
]
HUC_SIM_USUARIO = os.environ.get("HUC_SIM_USUARIO", "operador")
HUC_SIM_CLAVE = os.environ.get("HUC_SIM_CLAVE", "")
INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.sessions",
    "simulador.apps.SimuladorConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
    ]},
}]
DATABASES = {"default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.environ.get("HUC_SQLITE", str(BASE_DIR / "sesiones.sqlite3")),
}}
LANGUAGE_CODE = "es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static", RAIZ / "web" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
if os.environ.get("HUC_ENTORNO") == "contenedor":
    DEBUG = False
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_NAME = "huc_data_session"
CSRF_COOKIE_NAME = "huc_data_csrf"
