from django.urls import path

from . import views

urlpatterns = [
    path("agendar/", views.agendar, name="agendar"),
    path("painel/horario/", views.horario_funcionamento, name="horario_funcionamento"),
]
