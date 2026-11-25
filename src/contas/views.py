from functools import wraps

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import CadastroBarbeiroForm, CadastroClienteForm, LoginForm


def _cadastrar(request, form_class, template):
    if request.user.is_authenticated:
        return redirect("home")

    form = form_class(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        login(request, usuario, backend="django.contrib.auth.backends.ModelBackend")
        return redirect(usuario.destino_inicial())
    return render(request, template, {"form": form})


def cadastro_cliente(request):
    """RF01: cria a conta com papel cliente e já entra logado."""
    return _cadastrar(request, CadastroClienteForm, "contas/cadastro.html")


def cadastro_barbeiro(request):
    """RF04: cria o usuário com papel barbeiro e o perfil de barbeiro ligado a ele."""
    return _cadastrar(request, CadastroBarbeiroForm, "contas/cadastro_barbeiro.html")


class EntrarView(LoginView):
    """RF02/RF03: login por e-mail e senha. Cliente vai para a home; barbeiro, para o painel."""

    form_class = LoginForm
    template_name = "contas/entrar.html"
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        return reverse(self.request.user.destino_inicial())


class SairView(LogoutView):
    """RF02: encerra a sessão (só por POST, protegido por CSRF)."""


@login_required
def minha_conta(request):
    """Página restrita: exige login."""
    return render(request, "contas/minha_conta.html")


def barbeiro_requerido(view):
    """Exige login; quem não é barbeiro com perfil ativo recebe 403 (RF03)."""

    @login_required
    @wraps(view)
    def _view(request, *args, **kwargs):
        if not request.user.barbeiro_ativo:
            raise PermissionDenied("Área exclusiva de barbeiros.")
        return view(request, *args, **kwargs)

    return _view


@barbeiro_requerido
def painel_barbeiro(request):
    """RF03: painel do barbeiro. A agenda do dia em si entra com o RF09."""
    return render(request, "contas/painel_barbeiro.html", {"hoje": timezone.localdate()})
