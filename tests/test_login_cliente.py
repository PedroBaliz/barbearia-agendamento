"""RF02 – Como cliente, quero fazer login no sistema (issue #2)."""

import pytest
from django.urls import reverse

from contas.models import Usuario

ENTRAR = reverse("entrar")
SENHA = "corte-na-regua-9"

pytestmark = pytest.mark.django_db


@pytest.fixture
def cliente():
    return Usuario.objects.create_user(email="ana@exemplo.com", password=SENHA, nome="Ana Souza")


def logado(cliente_web):
    return "_auth_user_id" in cliente_web.session


def test_login_cliente(cliente_https, cliente):
    """Critério 1: e-mail e senha corretos levam à tela inicial do cliente, logado."""
    resposta = cliente_https.post(ENTRAR, {"username": "ana@exemplo.com", "password": SENHA})

    assert resposta.status_code == 302
    assert resposta.url == reverse("home")
    assert int(cliente_https.session["_auth_user_id"]) == cliente.pk
    assert "Olá, Ana Souza!" in cliente_https.get(reverse("home")).content.decode()


def test_login_aceita_email_com_maiusculas(cliente_https, cliente):
    cliente_https.post(ENTRAR, {"username": "  ANA@Exemplo.com ", "password": SENHA})
    assert logado(cliente_https)


def test_tela_de_login_abre(cliente_https):
    html = cliente_https.get(ENTRAR).content.decode()
    assert "Entrar" in html
    assert reverse("cadastro") in html


@pytest.mark.parametrize(
    ("email", "senha"),
    [("ana@exemplo.com", "senha-errada-1"), ("ninguem@exemplo.com", SENHA)],
    ids=["senha-errada", "email-inexistente"],
)
def test_credenciais_invalidas(cliente_https, cliente, email, senha):
    """Critério 2: mesma mensagem para e-mail ou senha errados, sem dizer qual."""
    resposta = cliente_https.post(ENTRAR, {"username": email, "password": senha})

    assert resposta.status_code == 200
    assert resposta.context["form"].non_field_errors() == ["E-mail ou senha inválidos."]
    assert not logado(cliente_https)


def test_conta_desativada_nao_entra(cliente_https, cliente):
    """Critério 3: conta desativada tem o acesso negado (com a mesma mensagem genérica)."""
    cliente.is_active = False
    cliente.save()

    resposta = cliente_https.post(ENTRAR, {"username": "ana@exemplo.com", "password": SENHA})

    assert resposta.status_code == 200
    assert "E-mail ou senha inválidos." in resposta.content.decode()
    assert not logado(cliente_https)


def test_sair_encerra_sessao(cliente_https, cliente):
    """Critério 4: depois de sair, páginas restritas pedem login."""
    cliente_https.force_login(cliente)
    assert cliente_https.get(reverse("minha_conta")).status_code == 200

    resposta = cliente_https.post(reverse("sair"))

    assert resposta.status_code == 302
    assert resposta.url == reverse("home")
    assert not logado(cliente_https)
    restrita = cliente_https.get(reverse("minha_conta"))
    assert restrita.status_code == 302
    assert restrita.url == f"{ENTRAR}?next={reverse('minha_conta')}"


def test_sair_nao_aceita_get(cliente_https, cliente):
    """Logout só por POST: um link ou imagem de outro site não derruba a sessão."""
    cliente_https.force_login(cliente)
    assert cliente_https.get(reverse("sair")).status_code == 405
    assert logado(cliente_https)


def test_login_volta_para_pagina_pedida(cliente_https, cliente):
    resposta = cliente_https.post(
        ENTRAR, {"username": "ana@exemplo.com", "password": SENHA, "next": reverse("minha_conta")}
    )
    assert resposta.url == reverse("minha_conta")


def test_login_ignora_next_externo(cliente_https, cliente):
    resposta = cliente_https.post(
        ENTRAR, {"username": "ana@exemplo.com", "password": SENHA, "next": "https://site-malicioso.com/"}
    )
    assert resposta.url == reverse("home")


def test_home_logada_mostra_sair_e_esconde_admin(cliente_https, cliente):
    cliente_https.force_login(cliente)
    html = cliente_https.get(reverse("home")).content.decode()
    assert reverse("sair") in html
    assert reverse("admin:index") not in html
