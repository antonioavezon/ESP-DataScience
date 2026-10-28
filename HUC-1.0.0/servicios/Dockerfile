FROM python:3.14.8-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HUC_ENTORNO=contenedor \
    DJANGO_SECRET_KEY=collectstatic-build \
    DJANGO_ALLOWED_HOSTS=localhost \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY servicios/requirements-runtime.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY codigo/web /app/web
COPY codigo/data /app/data
COPY codigo/proceso /app/proceso
COPY codigo/modelos_ia /app/modelos_ia
COPY codigo/datasets /app/datasets

FROM runtime AS visualizacion
WORKDIR /app/web
ENV PYTHONPATH=/app/web:/app
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 1 --threads 4 --timeout 120"]

FROM runtime AS data
WORKDIR /app/data/interfaces
ENV PYTHONPATH=/app/data/interfaces:/app:/app/web
RUN python manage.py collectstatic --noinput
EXPOSE 8001
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:8001 --workers 1 --threads 4 --timeout 120"]

FROM runtime AS proceso
WORKDIR /app
ENV PYTHONPATH=/app:/app/web:/app/datasets/en_uso/BES-jun/src
CMD ["python", "-m", "proceso.servicio"]

FROM runtime AS ia
WORKDIR /app
ENV PYTHONPATH=/app:/app/web \
    HUC_IA_BIND=0.0.0.0 \
    HUC_IA_PORT=8002
EXPOSE 8002
CMD ["python", "-m", "modelos_ia.servicio"]
