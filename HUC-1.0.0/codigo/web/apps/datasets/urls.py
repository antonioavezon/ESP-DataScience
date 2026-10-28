from django.urls import path

from apps.datasets import views

urlpatterns = [
    path("", views.lista, name="datasets"),
    path("<str:identificador>/", views.detalle, name="detalle_dataset"),
    path("<str:identificador>/seleccionar/", views.seleccionar, name="seleccionar_dataset"),
    path("<str:identificador>/pozos/<str:pozo_id>/", views.pozo, name="pozo"),
]
