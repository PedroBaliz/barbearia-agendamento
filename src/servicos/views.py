from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from contas.views import barbeiro_requerido

from .forms import ServicoForm
from .models import Servico


def _do_barbeiro(request, pk):
    """Só os serviços do próprio barbeiro: o de outro responde 404, sem revelar que existe."""
    return get_object_or_404(Servico, pk=pk, barbeiro=request.user.barbeiro)


@barbeiro_requerido
def meus_servicos(request):
    """RF12: lista dos serviços do barbeiro, ativos e desativados."""
    servicos = request.user.barbeiro.servicos.order_by("-ativo", "nome")
    return render(request, "servicos/meus_servicos.html", {"servicos": servicos})


@barbeiro_requerido
def novo_servico(request):
    form = ServicoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        servico = form.save(commit=False)
        servico.barbeiro = request.user.barbeiro
        servico.save()
        messages.success(request, f"Serviço “{servico.nome}” cadastrado.")
        return redirect("meus_servicos")
    return render(request, "servicos/form_servico.html", {"form": form, "titulo": "Novo serviço"})


@barbeiro_requerido
def editar_servico(request, pk):
    servico = _do_barbeiro(request, pk)
    form = ServicoForm(request.POST or None, instance=servico)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Serviço “{servico.nome}” atualizado.")
        return redirect("meus_servicos")
    contexto = {"form": form, "titulo": "Editar serviço", "servico": servico}
    return render(request, "servicos/form_servico.html", contexto)


@require_POST
@barbeiro_requerido
def alternar_servico(request, pk):
    """Desativa ou reativa. Nunca apaga: o histórico de agendamentos continua apontando para o serviço."""
    servico = _do_barbeiro(request, pk)
    servico.ativo = not servico.ativo
    servico.save(update_fields=["ativo"])
    acao = "reativado" if servico.ativo else "desativado"
    messages.success(request, f"Serviço “{servico.nome}” {acao}.")
    return redirect("meus_servicos")
