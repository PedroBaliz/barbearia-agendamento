from django.urls import path

from . import views

urlpatterns = [
    path("servicos/", views.lista_servicos, name="lista_servicos"),
    path("barbeiro/servicos/", views.meus_servicos, name="meus_servicos"),
    path("barbeiro/servicos/novo/", views.novo_servico, name="novo_servico"),
    path("barbeiro/servicos/<int:pk>/editar/", views.editar_servico, name="editar_servico"),
    path("barbeiro/servicos/<int:pk>/alternar/", views.alternar_servico, name="alternar_servico"),
]
