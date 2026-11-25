from django.contrib import admin
from django.urls import include, path

from core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("saude/", views.saude, name="saude"),
    path("contas/", include("contas.urls")),
    path("admin/", admin.site.urls),
]
