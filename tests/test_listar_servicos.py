"""RF13 – Como cliente, quero ver a lista de serviços disponíveis com preços (issue #13)."""

from decimal import Decimal

import pytest
from django.urls import reverse

from contas.models import Barbeiro, Usuario
from servicos.models import Servico

LISTA = reverse("lista_servicos")
AGENDAR = reverse("agendar")

pytestmark = pytest.mark.django_db


def criar_barbeiro(email, nome):
    usuario = Usuario.objects.create_user(email=email, password="x", nome=nome, papel="barbeiro")
    return Barbeiro.objects.create(usuario=usuario, especialidade="Cortes")


@pytest.fixture
def bruno():
    return criar_barbeiro("bruno@exemplo.com", "Bruno Lima")


@pytest.fixture
def caio():
    return criar_barbeiro("caio@exemplo.com", "Caio Reis")


@pytest.fixture
def corte(bruno):
    return Servico.objects.create(
        barbeiro=bruno, nome="Corte degradê", descricao="Máquina e tesoura", preco=Decimal("45.00"), duracao_min=40
    )


def nomes(resposta):
    return [s.nome for s in resposta.context["servicos"]]


def test_listar_servicos(cliente_https, corte):
    """Critério 1: sem login, vejo os serviços ativos com nome, descrição, preço em reais e duração."""
    resposta = cliente_https.get(LISTA)

    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "Corte degradê" in html
    assert "Máquina e tesoura" in html
    assert "R$ 45,00" in html
    assert "40 min" in html
    assert "Bruno Lima" in html


def test_inativos_nao_aparecem(cliente_https, bruno, caio, corte):
    """Critério 2: serviço inativo e serviço de barbeiro inativo não aparecem."""
    Servico.objects.create(barbeiro=bruno, nome="Serviço desativado", preco=10, duracao_min=10, ativo=False)
    Servico.objects.create(barbeiro=caio, nome="Corte do Caio", preco=30, duracao_min=30)
    Barbeiro.objects.filter(pk=caio.pk).update(ativo=False)

    resposta = cliente_https.get(LISTA)

    assert nomes(resposta) == ["Corte degradê"]
    assert "Caio Reis" not in resposta.content.decode()


def test_conta_do_barbeiro_desativada_tambem_esconde(cliente_https, corte, bruno):
    Usuario.objects.filter(pk=bruno.usuario_id).update(is_active=False)
    assert nomes(cliente_https.get(LISTA)) == []


def test_filtrar_por_barbeiro(cliente_https, bruno, caio, corte):
    """Critério 3: filtro por barbeiro."""
    Servico.objects.create(barbeiro=caio, nome="Barba", preco=30, duracao_min=20)

    assert nomes(cliente_https.get(LISTA)) == ["Barba", "Corte degradê"]
    filtrada = cliente_https.get(LISTA, {"barbeiro": caio.pk})
    assert nomes(filtrada) == ["Barba"]
    assert f'value="{caio.pk}" selected' in filtrada.content.decode()


@pytest.mark.parametrize("valor", ["abc", "", "999999"])
def test_filtro_invalido_nao_quebra(cliente_https, corte, valor):
    resposta = cliente_https.get(LISTA, {"barbeiro": valor})
    assert resposta.status_code == 200


def test_filtro_lista_so_barbeiros_disponiveis(cliente_https, bruno, caio):
    Barbeiro.objects.filter(pk=caio.pk).update(ativo=False)
    barbeiros = list(cliente_https.get(LISTA).context["barbeiros"])
    assert barbeiros == [bruno]


def test_iniciar_agendamento_com_servico_selecionado(cliente_https, corte):
    """Critério 4: a partir do serviço, o agendamento começa com ele já selecionado."""
    link = f"{AGENDAR}?servico={corte.pk}"
    assert link in cliente_https.get(LISTA).content.decode()

    cliente = Usuario.objects.create_user(email="ana@exemplo.com", password="x", nome="Ana")
    cliente_https.force_login(cliente)
    resposta = cliente_https.get(link)

    assert resposta.status_code == 200
    assert resposta.context["servico"] == corte
    assert f'data-servico="{corte.pk}"' in resposta.content.decode()


def test_agendar_sem_login_vai_ao_login_e_volta(cliente_https, corte):
    resposta = cliente_https.get(AGENDAR, {"servico": corte.pk})
    assert resposta.status_code == 302
    assert resposta.url.startswith(reverse("entrar"))
    assert "next=/agendar/%3Fservico%3D" in resposta.url


@pytest.mark.parametrize("valor", [None, "abc", "999999"])
def test_agendar_servico_invalido_404(cliente_https, valor):
    cliente_https.force_login(Usuario.objects.create_user(email="ana@exemplo.com", password="x", nome="Ana"))
    params = {} if valor is None else {"servico": valor}
    assert cliente_https.get(AGENDAR, params).status_code == 404


def test_agendar_servico_desativado_404(cliente_https, corte):
    Servico.objects.filter(pk=corte.pk).update(ativo=False)
    cliente_https.force_login(Usuario.objects.create_user(email="ana@exemplo.com", password="x", nome="Ana"))
    assert cliente_https.get(AGENDAR, {"servico": corte.pk}).status_code == 404


def test_lista_vazia(cliente_https):
    assert "Nenhum serviço disponível" in cliente_https.get(LISTA).content.decode()


def test_home_tem_link_para_servicos(cliente_https):
    assert LISTA in cliente_https.get(reverse("home")).content.decode()
