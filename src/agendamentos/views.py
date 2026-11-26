from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect, render

from contas.views import admin_requerido
from servicos.models import Servico

from .forms import DiaFuncionamentoForm
from .models import HorarioFuncionamento


@login_required
def agendar(request):
    """Início do agendamento com o serviço já escolhido (RF13).

    A escolha de data e horário entra com o RF05/RF06. Quem não está logado vai para o login
    e volta para cá depois de entrar, com o serviço preservado no `next`.
    """
    try:
        servico = Servico.objects.disponiveis().select_related("barbeiro__usuario").get(pk=request.GET.get("servico"))
    except (Servico.DoesNotExist, ValueError, TypeError) as erro:
        raise Http404("Serviço indisponível.") from erro
    return render(request, "agendamentos/agendar.html", {"servico": servico})


@admin_requerido
def horario_funcionamento(request):
    """RF18: o admin define, para cada dia da semana, se abre e o horário de abertura e fechamento.

    Os 7 dias são salvos juntos, numa transação: se um dia tiver erro, nenhum é gravado.
    Só a tabela horario_funcionamento é alterada; agendamentos existentes não mudam.
    """
    atuais = {h.dia_semana: h for h in HorarioFuncionamento.objects.all()}
    forms = []
    for dia, nome in HorarioFuncionamento.DiaSemana.choices:
        h = atuais.get(dia)
        inicial = {"aberto": h.aberto, "abertura": h.abertura, "fechamento": h.fechamento} if h else {}
        forms.append(
            DiaFuncionamentoForm(request.POST or None, prefix=f"dia{dia}", initial=inicial, dia=dia, nome_dia=nome)
        )

    if request.method == "POST":
        if all(form.is_valid() for form in forms):
            with transaction.atomic():
                for form in forms:
                    HorarioFuncionamento.objects.update_or_create(dia_semana=form.dia, defaults=form.cleaned_data)
            messages.success(request, "Horário de funcionamento salvo.")
            return redirect("horario_funcionamento")
        return render(request, "agendamentos/horario_funcionamento.html", {"forms": forms, "tem_erro": True})
    return render(request, "agendamentos/horario_funcionamento.html", {"forms": forms})
