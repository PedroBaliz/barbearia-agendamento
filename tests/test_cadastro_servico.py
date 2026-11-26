"""RF12 – Como barbeiro, quero cadastrar os serviços que ofereço com nome, preço e duração (issue #12)."""

from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.urls import reverse

from contas.models import Barbeiro, Usuario
from servicos.models import Servico

NOVO = reverse("novo_servico")
LISTA = reverse("meus_servicos")
DADOS = {"nome": "Corte degradê", "descricao": "Máquina e tesoura", "preco": "45.00", "duracao_min": "40"}

pytestmark = pytest.mark.django_db


def criar_barbeiro(email, nome="Bruno"):
    usuario = Usuario.objects.create_user(email=email, password="x", nome=nome, papel="barbeiro")
    return Barbeiro.objects.create(usuario=usuario, especialidade="Cortes")


@pytest.fixture
def barbeiro():
    return criar_barbeiro("bruno@exemplo.com")


@pytest.fixture
def logado(cliente_https, barbeiro):
    cliente_https.force_login(barbeiro.usuario)
    return cliente_https


def test_cadastrar_servico(logado, barbeiro):
    """Critério 1: serviço válido aparece na lista do barbeiro e fica disponível para agendamento."""
    resposta = logado.post(NOVO, DADOS)

    assert resposta.status_code == 302
    assert resposta.url == LISTA
    servico = Servico.objects.get()
    assert servico.barbeiro == barbeiro
    assert servico.preco == Decimal("45.00")
    assert servico.duracao_min == 40
    assert servico.ativo
    assert list(Servico.objects.disponiveis()) == [servico]

    html = logado.get(LISTA).content.decode()
    assert "Corte degradê" in html
    assert "Serviço “Corte degradê” cadastrado." in html


@pytest.mark.parametrize(
    ("campo", "valor", "mensagem"),
    [
        ("preco", "0", "O preço precisa ser maior que zero."),
        ("preco", "-10", "O preço precisa ser maior que zero."),
        ("preco", "abc", "Informe um valor em reais, como 35,00."),
        ("duracao_min", "4", "A duração mínima é 5 minutos."),
        ("duracao_min", "481", "A duração máxima é 480 minutos."),
        ("nome", "", "Este campo é obrigatório."),
    ],
)
def test_dado_invalido_mostra_erro_no_campo(logado, campo, valor, mensagem):
    """Critério 2: preço ou duração inválidos mostram o erro no campo correspondente."""
    resposta = logado.post(NOVO, {**DADOS, campo: valor})

    assert resposta.status_code == 200
    assert resposta.context["form"].errors[campo] == [mensagem]
    assert f'aria-describedby="id_{campo}-erro"' in resposta.content.decode()
    assert not Servico.objects.exists()


@pytest.mark.parametrize("duracao", ["5", "480"])
def test_limites_de_duracao_aceitos(logado, duracao):
    assert logado.post(NOVO, {**DADOS, "duracao_min": duracao}).status_code == 302


def test_editar_servico(logado, barbeiro):
    """Critério 3: o barbeiro edita os próprios serviços."""
    servico = Servico.objects.create(barbeiro=barbeiro, nome="Barba", preco=30, duracao_min=20)

    resposta = logado.post(reverse("editar_servico", args=[servico.pk]), {**DADOS, "nome": "Barba completa"})

    assert resposta.url == LISTA
    servico.refresh_from_db()
    assert servico.nome == "Barba completa"
    assert servico.barbeiro == barbeiro


def test_desativar_e_reativar(logado, barbeiro):
    """Critério 3: serviço desativado some da lista dos clientes, mas continua existindo (histórico)."""
    servico = Servico.objects.create(barbeiro=barbeiro, nome="Barba", preco=30, duracao_min=20)
    alternar = reverse("alternar_servico", args=[servico.pk])

    logado.post(alternar)
    servico.refresh_from_db()
    assert not servico.ativo
    assert not Servico.objects.disponiveis().exists()
    assert Servico.objects.filter(pk=servico.pk).exists()
    assert "Desativado" in logado.get(LISTA).content.decode()

    logado.post(alternar)
    servico.refresh_from_db()
    assert servico.ativo


def test_desativar_so_por_post(logado, barbeiro):
    servico = Servico.objects.create(barbeiro=barbeiro, nome="Barba", preco=30, duracao_min=20)
    assert logado.get(reverse("alternar_servico", args=[servico.pk])).status_code == 405


def test_nao_edita_servico_de_outro_barbeiro(logado):
    """Critério 4: serviço de outro barbeiro responde 404, sem revelar que existe."""
    outro = criar_barbeiro("outro@exemplo.com", nome="Outro")
    servico = Servico.objects.create(barbeiro=outro, nome="Navalha", preco=50, duracao_min=30)

    assert logado.get(reverse("editar_servico", args=[servico.pk])).status_code == 404
    assert logado.post(reverse("editar_servico", args=[servico.pk]), DADOS).status_code == 404
    assert logado.post(reverse("alternar_servico", args=[servico.pk])).status_code == 404
    servico.refresh_from_db()
    assert servico.nome == "Navalha"
    assert servico.ativo


def test_lista_mostra_so_os_meus(logado, barbeiro):
    Servico.objects.create(barbeiro=barbeiro, nome="Meu corte", preco=40, duracao_min=30)
    Servico.objects.create(barbeiro=criar_barbeiro("o@exemplo.com"), nome="Corte do outro", preco=40, duracao_min=30)

    html = logado.get(LISTA).content.decode()
    assert "Meu corte" in html
    assert "Corte do outro" not in html


def test_barbeiro_nao_escolhe_o_dono_pelo_formulario(logado, barbeiro):
    outro = criar_barbeiro("o@exemplo.com")
    logado.post(NOVO, {**DADOS, "barbeiro": outro.pk})
    assert Servico.objects.get().barbeiro == barbeiro


def test_cliente_e_visitante_nao_cadastram(cliente_https):
    assert cliente_https.get(NOVO).status_code == 302
    cliente = Usuario.objects.create_user(email="ana@exemplo.com", password="x", nome="Ana")
    cliente_https.force_login(cliente)
    assert cliente_https.get(NOVO).status_code == 403
    assert cliente_https.post(NOVO, DADOS).status_code == 403
    assert not Servico.objects.exists()


def test_disponiveis_exclui_barbeiro_inativo(barbeiro):
    Servico.objects.create(barbeiro=barbeiro, nome="Corte", preco=40, duracao_min=30)
    Barbeiro.objects.filter(pk=barbeiro.pk).update(ativo=False)
    assert not Servico.objects.disponiveis().exists()


@pytest.mark.parametrize(("campo", "valor"), [("preco", 0), ("duracao_min", 4), ("duracao_min", 481)])
def test_banco_recusa_valor_invalido(barbeiro, campo, valor):
    """As regras também valem no banco (CheckConstraint), não só no formulário."""
    dados = {"barbeiro": barbeiro, "nome": "X", "preco": 10, "duracao_min": 30, campo: valor}
    with pytest.raises(IntegrityError), transaction.atomic():
        Servico.objects.create(**dados)


@pytest.mark.parametrize(("minutos", "texto"), [(30, "30 min"), (60, "1h"), (90, "1h30"), (125, "2h05")])
def test_duracao_legivel(minutos, texto):
    assert Servico(duracao_min=minutos).duracao_legivel == texto


def test_painel_tem_link_para_servicos(logado):
    assert LISTA in logado.get(reverse("painel_barbeiro")).content.decode()
