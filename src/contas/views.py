from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import CadastroClienteForm


def cadastro_cliente(request):
    """RF01: cria a conta com papel cliente e já entra logado."""
    if request.user.is_authenticated:
        return redirect("home")

    form = CadastroClienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        login(request, usuario, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("home")
    return render(request, "contas/cadastro.html", {"form": form})
