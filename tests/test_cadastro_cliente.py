"""RF01 – Como cliente, quero me cadastrar com nome, e-mail e senha (issue #1)."""

import pytest
from django.test import Client
from django.urls import reverse

from contas.models import Usuario

URL = reverse("cadastro")
DADOS = {"nome": "Ana Souza", "email": "ana@exemplo.com", "senha": "corte-na-regua-9"}

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    """Cliente sempre em HTTPS, como em produção atrás da Vercel (no CI, DEBUG=False liga o SECURE_SSL_REDIRECT)."""
    return Client(HTTP_X_FORWARDED_PROTO="https", **{"wsgi.url_scheme": "https"})


def test_cadastro_cliente(client):
    """Critério 1: conta criada com papel cliente e o usuário já entra logado na tela inicial."""
    resposta = client.post(URL, DADOS)

    assert resposta.status_code == 302
    assert resposta.url == reverse("home")
    usuario = Usuario.objects.get(email="ana@exemplo.com")
    assert usuario.nome == "Ana Souza"
    assert usuario.papel == Usuario.Papel.CLIENTE
    assert not usuario.is_staff
    assert int(client.session["_auth_user_id"]) == usuario.pk

    home = client.get(reverse("home"))
    assert "Olá, Ana Souza!" in home.content.decode()


def test_tela_de_cadastro_abre(client):
    resposta = client.get(URL)
    assert resposta.status_code == 200
    assert "Criar conta" in resposta.content.decode()


@pytest.mark.parametrize("email", ["ana@exemplo.com", "ANA@Exemplo.com"])
def test_email_ja_cadastrado(client, email):
    """Critério 2: e-mail repetido (sem diferenciar maiúsculas) mostra a mensagem e não cria conta."""
    Usuario.objects.create_user(email="ana@exemplo.com", password="outra-senha-123", nome="Ana")

    resposta = client.post(URL, {**DADOS, "email": email})

    assert resposta.status_code == 200
    assert "E-mail já cadastrado" in resposta.content.decode()
    assert Usuario.objects.count() == 1


@pytest.mark.parametrize("campo", ["nome", "email", "senha"])
def test_campo_em_branco(client, campo):
    """Critério 3: campo em branco fica destacado com a mensagem do erro."""
    resposta = client.post(URL, {**DADOS, campo: ""})

    assert resposta.status_code == 200
    form = resposta.context["form"]
    assert form.errors[campo] == ["Este campo é obrigatório."]
    assert "is-invalid" in resposta.content.decode()
    assert not Usuario.objects.exists()


@pytest.mark.parametrize(
    ("campo", "valor"),
    [("email", "ana-sem-arroba"), ("senha", "curta1"), ("senha", "12345678901")],
)
def test_dado_invalido(client, campo, valor):
    """Critério 3: e-mail inválido ou senha fraca (menos de 8 caracteres, só números) não cria conta."""
    resposta = client.post(URL, {**DADOS, campo: valor})

    assert resposta.status_code == 200
    assert campo in resposta.context["form"].errors
    assert not Usuario.objects.exists()


def test_senha_gravada_como_hash(client):
    """Critério 4: a senha é gravada só como hash (bcrypt, RNF02)."""
    client.post(URL, DADOS)
    usuario = Usuario.objects.get(email="ana@exemplo.com")

    assert usuario.password != DADOS["senha"]
    assert DADOS["senha"] not in usuario.password
    assert usuario.password.startswith("bcrypt_sha256$")
    assert usuario.check_password(DADOS["senha"])


def test_usuario_logado_volta_para_home(client):
    usuario = Usuario.objects.create_user(email="ja@exemplo.com", password="senha-forte-123", nome="Já")
    client.force_login(usuario)

    resposta = client.get(URL)

    assert resposta.status_code == 302
    assert resposta.url == reverse("home")
