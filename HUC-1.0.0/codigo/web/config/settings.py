import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
HUC_ROOT = BASE_DIR.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or "clave-solo-desarrollo-local-huc"
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
if not DEBUG and SECRET_KEY == "clave-solo-desarrollo-local-huc":
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured("Defina DJANGO_SECRET_KEY cuando DJANGO_DEBUG no es 1.")

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

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.sessions",
    "django.contrib.messages",
    "apps.core",
    "apps.datasets",
    "apps.evaluaciones",
    "apps.asistente_ia",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context.navegacion",
            ],
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("HUC_SQLITE", str(BASE_DIR / "db.sqlite3")),
    }
}

LANGUAGE_CODE = "es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
if os.environ.get("HUC_ENTORNO") == "contenedor":
    DEBUG = False
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

DATA_UPLOAD_MAX_MEMORY_SIZE = 256 * 1024
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
