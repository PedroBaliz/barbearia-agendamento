from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import CadastroClienteForm, LoginForm


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


class EntrarView(LoginView):
    """RF02: login por e-mail e senha. Conta desativada não entra."""

    form_class = LoginForm
    template_name = "contas/entrar.html"
    redirect_authenticated_user = True


class SairView(LogoutView):
    """RF02: encerra a sessão (só por POST, protegido por CSRF)."""


@login_required
def minha_conta(request):
    """Página restrita: exige login."""
    return render(request, "contas/minha_conta.html")
