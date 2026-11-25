from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Barbeiro, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    ordering = ["email"]
    list_display = ["email", "nome", "papel", "is_active", "is_staff"]
    list_filter = ["papel", "is_active", "is_staff"]
    search_fields = ["email", "nome"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Dados pessoais", {"fields": ["nome", "telefone", "papel"]}),
        ("Permissões", {"fields": ["is_active", "is_staff", "is_superuser", "groups", "user_permissions"]}),
        ("Datas", {"fields": ["last_login", "date_joined"]}),
    ]
    add_fieldsets = [
        (None, {"classes": ["wide"], "fields": ["email", "nome", "papel", "password1", "password2"]}),
    ]


@admin.register(Barbeiro)
class BarbeiroAdmin(admin.ModelAdmin):
    list_display = ["usuario", "especialidade", "ativo"]
    list_filter = ["ativo"]
    search_fields = ["usuario__nome", "usuario__email", "especialidade"]
    list_select_related = ["usuario"]
    raw_id_fields = ["usuario"]
