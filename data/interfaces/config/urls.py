from django.urls import path

from simulador import views

urlpatterns = [
    path("", views.inicio, name="simulador"),
    path("api/sesion/", views.sesion, name="sesion"),
    path("api/acceder/", views.acceder, name="acceder"),
    path("api/cerrar-sesion/", views.cerrar_sesion, name="cerrar_sesion"),
    path("api/pozos/", views.pozos, name="pozos"),
    path("api/pozos/<str:pozo_id>/base/", views.base, name="base"),
    path("api/pozos/<str:pozo_id>/aplicar/", views.aplicar, name="aplicar"),
    path("api/pozos/<str:pozo_id>/restaurar/", views.restaurar, name="restaurar"),
    path("api/pozos/<str:pozo_id>/acuse/<str:evaluacion_id>/", views.acuse, name="acuse"),
    path("api/pozos/<str:pozo_id>/fase/", views.fase, name="fase"),
    path("api/pozos/<str:pozo_id>/automatica/", views.automatica, name="automatica"),
]
