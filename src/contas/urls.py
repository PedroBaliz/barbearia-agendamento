from django.urls import path

from . import views

urlpatterns = [
    path("cadastro/", views.cadastro_cliente, name="cadastro"),
    path("entrar/", views.EntrarView.as_view(), name="entrar"),
    path("sair/", views.SairView.as_view(), name="sair"),
    path("minha-conta/", views.minha_conta, name="minha_conta"),
]
