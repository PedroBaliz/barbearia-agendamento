from django.contrib import admin
from django.urls import include, path

from contas.views import painel_barbeiro
from core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("saude/", views.saude, name="saude"),
    path("contas/", include("contas.urls")),
    path("barbeiro/", painel_barbeiro, name="painel_barbeiro"),
    path("", include("servicos.urls")),
    path("", include("agendamentos.urls")),
    path("admin/", admin.site.urls),
]
