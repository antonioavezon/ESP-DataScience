from django.urls import path

from apps.evaluaciones import views

urlpatterns = [
    path("", views.indice, name="evaluaciones"),
    path("ejecutar/", views.ejecutar, name="ejecutar_evaluacion"),
]
