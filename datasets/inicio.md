En Fedora 43, Ollama está como servicio de systemd (ollama.service, binario en /usr/local/bin/ollama) y la aplicación usa el modelo qwen3:4b-instruct-2507-q4_K_M en http://127.0.0.1:11434. Hacen falta dos terminales: una deja el modelo cargado y la otra levanta Django.

Terminal 1. Servicio y modelo

El primer comando arranca el servicio de Ollama si no está corriendo. El segundo carga el modelo en memoria y lo deja residente hasta que se detenga el servicio.

sudo systemctl start ollama
curl -s http://127.0.0.1:11434/api/generate -d '{"model":"qwen3:4b-instruct-2507-q4_K_M","prompt":"","keep_alive":-1}'



Terminal 2. Aplicación

Este comando arranca el servidor de desarrollo de HUC y lo deja escuchando en el puerto 8000.

cd /home/antonio/projects/HUC/web
/home/antonio/projects/HUC/.venv/bin/python manage.py runserver 127.0.0.1:8000

La aplicación queda en http://127.0.0.1:8000/ y el asistente en http://127.0.0.1:8000/asistente/.