from django.contrib import admin

from .models import Servico


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ["nome", "barbeiro", "preco", "duracao_min", "ativo"]
    list_filter = ["ativo", "barbeiro"]
    search_fields = ["nome", "barbeiro__usuario__nome"]
    list_select_related = ["barbeiro__usuario"]
