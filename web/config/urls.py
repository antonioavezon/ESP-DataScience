from django.urls import include, path

urlpatterns = [
    path("", include("apps.core.urls")),
    path("datasets/", include("apps.datasets.urls")),
    path("asistente/", include("apps.asistente_ia.urls")),
]
