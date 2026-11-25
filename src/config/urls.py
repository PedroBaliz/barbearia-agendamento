from django.contrib import admin
from django.urls import path

from core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("saude/", views.saude, name="saude"),
    path("admin/", admin.site.urls),
]
