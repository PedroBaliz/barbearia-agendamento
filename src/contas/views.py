from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import CadastroBarbeiroForm, CadastroClienteForm, LoginForm


def _cadastrar(request, form_class, template):
    if request.user.is_authenticated:
        return redirect("home")

    form = form_class(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        login(request, usuario, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("home")
    return render(request, template, {"form": form})


def cadastro_cliente(request):
    """RF01: cria a conta com papel cliente e já entra logado."""
    return _cadastrar(request, CadastroClienteForm, "contas/cadastro.html")


def cadastro_barbeiro(request):
    """RF04: cria o usuário com papel barbeiro e o perfil de barbeiro ligado a ele."""
    return _cadastrar(request, CadastroBarbeiroForm, "contas/cadastro_barbeiro.html")


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
