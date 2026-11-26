from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from servicos.models import Servico


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
