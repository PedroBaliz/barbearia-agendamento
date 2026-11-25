"""Testes da issue #34: o ambiente sobe, responde e segue os requisitos não funcionais."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.test import override_settings
from django.urls import reverse


def test_home_responde(cliente_web):
    resposta = cliente_web.get(reverse("home"), secure=True)
    assert resposta.status_code == 200
    assert "BarberBook" in resposta.content.decode()


def test_home_e_responsiva(cliente_web):
    """RNF03: a página declara viewport para celular."""
    html = cliente_web.get(reverse("home"), secure=True).content.decode()
    assert 'name="viewport"' in html


@pytest.mark.django_db
def test_saude_responde_ok(cliente_web):
    resposta = cliente_web.get(reverse("saude"))
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok", "banco": "ok"}


@pytest.mark.django_db
def test_usuario_faz_login_por_email():
    usuario = get_user_model().objects.create_user(email="Cliente@Exemplo.com", password="senha-forte-123", nome="Ana")
    assert get_user_model().USERNAME_FIELD == "email"
    assert usuario.email == "Cliente@exemplo.com"  # domínio normalizado
    assert usuario.papel == "cliente"


@pytest.mark.django_db
def test_senha_usa_bcrypt():
    """RNF02: senhas armazenadas com hash bcrypt, nunca em texto."""
    usuario = get_user_model().objects.create_user(email="b@exemplo.com", password="senha-forte-123", nome="Bruno")
    assert usuario.password != "senha-forte-123"
    assert identify_hasher(usuario.password).algorithm == "bcrypt_sha256"
    assert usuario.check_password("senha-forte-123")


@pytest.mark.django_db
def test_superusuario_e_admin():
    admin = get_user_model().objects.create_superuser(
        email="admin@exemplo.com", password="senha-forte-123", nome="Admin"
    )
    assert admin.is_staff and admin.is_superuser
    assert admin.papel == "admin"


@pytest.mark.django_db
def test_email_obrigatorio():
    with pytest.raises(ValueError):
        get_user_model().objects.create_user(email="", password="x", nome="Sem e-mail")


@pytest.mark.django_db
@override_settings(SECURE_SSL_REDIRECT=True, SECURE_REDIRECT_EXEMPT=[r"^saude/$"])
def test_http_redireciona_para_https_menos_healthcheck(cliente_web):
    """Em produção, HTTP vai para HTTPS; o healthcheck interno do Railway (HTTP) continua respondendo."""
    resposta = cliente_web.get(reverse("home"))
    assert resposta.status_code == 301
    assert resposta["Location"].startswith("https://")
    assert cliente_web.get(reverse("saude")).status_code == 200
