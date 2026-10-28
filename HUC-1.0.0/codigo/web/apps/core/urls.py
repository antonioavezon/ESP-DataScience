from django.urls import path

from apps.core import api_consola, views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("acerca/", views.acerca, name="acerca"),
    path("api/consola/estados/", api_consola.estados, name="api_estados"),
    path("api/consola/pozos/", api_consola.pozos, name="api_pozos"),
    path("api/consola/pozos/<str:pozo_id>/escenario/", api_consola.escenario, name="api_escenario"),
    path("api/consola/pozos/<str:pozo_id>/resultado/", api_consola.resultado, name="api_resultado"),
    path("api/consola/pozos/<str:pozo_id>/explicacion/", api_consola.explicacion, name="api_explicacion"),
]
