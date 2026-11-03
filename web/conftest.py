import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DJANGO_DEBUG", "1")
hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")
if "testserver" not in hosts.split(","):
    os.environ["DJANGO_ALLOWED_HOSTS"] = "testserver," + hosts
django.setup()
