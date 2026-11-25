"""RF03 – Como barbeiro, quero fazer login com minha conta (issue #3)."""

import pytest
from django.urls import reverse

from contas.models import Barbeiro, Usuario

ENTRAR = reverse("entrar")
PAINEL = reverse("painel_barbeiro")
SENHA = "navalha-afiada-7"

pytestmark = pytest.mark.django_db


@pytest.fixture
def barbeiro():
    usuario = Usuario.objects.create_user(
        email="bruno@exemplo.com", password=SENHA, nome="Bruno Lima", papel="barbeiro"
    )
    Barbeiro.objects.create(usuario=usuario, especialidade="Degradê e barba")
    return usuario


@pytest.fixture
def cliente():
    return Usuario.objects.create_user(email="ana@exemplo.com", password=SENHA, nome="Ana Souza")


def entrar(cliente_web, email, senha=SENHA):
    return cliente_web.post(ENTRAR, {"username": email, "password": senha})


def test_login_barbeiro(cliente_https, barbeiro):
    """Critério 1: barbeiro ativo entra e vai para o painel (agenda do dia)."""
    resposta = entrar(cliente_https, "bruno@exemplo.com")

    assert resposta.status_code == 302
    assert resposta.url == PAINEL
    painel = cliente_https.get(PAINEL)
    assert painel.status_code == 200
    html = painel.content.decode()
    assert "Agenda do dia" in html
    assert "Degradê e barba" in html


def test_cliente_nao_acessa_painel(cliente_https, cliente):
    """Critério 2: cliente logado recebe 403 no painel do barbeiro."""
    cliente_https.force_login(cliente)

    resposta = cliente_https.get(PAINEL)

    assert resposta.status_code == 403
    assert "Acesso negado" in resposta.content.decode()


def test_cliente_continua_indo_para_home(cliente_https, cliente):
    assert entrar(cliente_https, "ana@exemplo.com").url == reverse("home")


def test_visitante_no_painel_vai_para_login(cliente_https):
    resposta = cliente_https.get(PAINEL)
    assert resposta.status_code == 302
    assert resposta.url == f"{ENTRAR}?next={PAINEL}"


def test_perfil_inativo_nao_entra(cliente_https, barbeiro):
    """Critério 3: perfil de barbeiro inativo tem o login e o painel negados."""
    Barbeiro.objects.filter(usuario=barbeiro).update(ativo=False)

    resposta = entrar(cliente_https, "bruno@exemplo.com")

    assert resposta.status_code == 200
    assert resposta.context["form"].non_field_errors() == ["Seu perfil de barbeiro está inativo. Fale com a barbearia."]
    assert "_auth_user_id" not in cliente_https.session


def test_perfil_desativado_com_sessao_aberta_perde_o_painel(cliente_https, barbeiro):
    """Se o perfil for desativado com o barbeiro já logado, o painel passa a negar o acesso."""
    cliente_https.force_login(barbeiro)
    assert cliente_https.get(PAINEL).status_code == 200

    Barbeiro.objects.filter(usuario=barbeiro).update(ativo=False)

    assert cliente_https.get(PAINEL).status_code == 403


def test_barbeiro_sem_perfil_nao_entra(cliente_https):
    Usuario.objects.create_user(email="sem@exemplo.com", password=SENHA, nome="Sem perfil", papel="barbeiro")
    assert entrar(cliente_https, "sem@exemplo.com").status_code == 200
    assert "_auth_user_id" not in cliente_https.session


def test_senha_errada_mantem_mensagem_generica(cliente_https, barbeiro):
    Barbeiro.objects.filter(usuario=barbeiro).update(ativo=False)
    resposta = entrar(cliente_https, "bruno@exemplo.com", senha=SENHA[::-1])
    assert resposta.context["form"].non_field_errors() == ["E-mail ou senha inválidos."]


def test_cadastro_de_barbeiro_leva_ao_painel(cliente_https):
    resposta = cliente_https.post(
        reverse("cadastro_barbeiro"),
        {"nome": "Caio", "email": "caio@exemplo.com", "especialidade": "Navalha", "senha": SENHA},
    )
    assert resposta.url == PAINEL


def test_barbeiro_logado_em_entrar_vai_ao_painel(cliente_https, barbeiro):
    cliente_https.force_login(barbeiro)
    assert cliente_https.get(ENTRAR).url == PAINEL


def test_home_do_barbeiro_tem_link_para_painel(cliente_https, barbeiro, cliente):
    cliente_https.force_login(barbeiro)
    assert PAINEL in cliente_https.get(reverse("home")).content.decode()
    cliente_https.force_login(cliente)
    assert PAINEL not in cliente_https.get(reverse("home")).content.decode()
