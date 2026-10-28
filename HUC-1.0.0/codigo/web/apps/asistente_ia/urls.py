from django.urls import path

from apps.asistente_ia import views

urlpatterns = [
    path("", views.consultar, name="asistente"),
    path("enviar/", views.enviar, name="enviar_consulta"),
    path("borrar/", views.borrar, name="borrar_consulta"),
    path("configuracion/", views.configuracion_ia, name="configuracion_ia"),
]
