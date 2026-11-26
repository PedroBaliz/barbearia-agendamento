from django.contrib import admin

from .models import HorarioFuncionamento


@admin.register(HorarioFuncionamento)
class HorarioFuncionamentoAdmin(admin.ModelAdmin):
    list_display = ["dia_semana", "aberto", "abertura", "fechamento"]
    list_editable = ["aberto", "abertura", "fechamento"]
