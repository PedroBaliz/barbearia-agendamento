"""RF18 – Como admin, quero configurar o horário de funcionamento da barbearia (issue #18)."""

from datetime import date, time

import pytest
from django.db import IntegrityError, transaction
from django.urls import reverse

from agendamentos.models import HorarioFuncionamento
from contas.models import Barbeiro, Usuario
from servicos.models import Servico

URL = reverse("horario_funcionamento")
SEGUNDA = date(2026, 11, 30)  # segunda-feira
DOMINGO = date(2026, 12, 6)

pytestmark = pytest.mark.django_db


def semana(**por_dia):
    """POST dos 7 dias: segunda a sábado 09:00–19:00, domingo fechado; `por_dia` sobrescreve campos."""
    dados = {}
    for dia in range(7):
        aberto = dia != 6
        dados[f"dia{dia}-abertura"] = "09:00" if aberto else ""
        dados[f"dia{dia}-fechamento"] = "19:00" if aberto else ""
        if aberto:
            dados[f"dia{dia}-aberto"] = "on"
    for chave, valor in por_dia.items():
        dia, campo = chave.split("_", 1)
        chave_form = f"dia{dia[1:]}-{campo}"
        if valor is None:
            dados.pop(chave_form, None)
        else:
            dados[chave_form] = valor
    return dados


@pytest.fixture
def admin():
    return Usuario.objects.create_superuser(email="admin@exemplo.com", password="x", nome="Admin")


@pytest.fixture
def logado(cliente_https, admin):
    cliente_https.force_login(admin)
    return cliente_https


def test_horario_funcionamento(logado):
    """Critério 1: o admin define, para cada dia, se abre e o horário; a configuração é salva."""
    resposta = logado.post(URL, semana(d5_abertura="08:00", d5_fechamento="14:00"))

    assert resposta.status_code == 302
    assert HorarioFuncionamento.objects.count() == 7
    segunda = HorarioFuncionamento.objects.get(dia_semana=0)
    assert (segunda.aberto, segunda.abertura, segunda.fechamento) == (True, time(9), time(19))
    sabado = HorarioFuncionamento.objects.get(dia_semana=5)
    assert (sabado.abertura, sabado.fechamento) == (time(8), time(14))
    domingo = HorarioFuncionamento.objects.get(dia_semana=6)
    assert (domingo.aberto, domingo.abertura, domingo.fechamento) == (False, None, None)

    tela = logado.get(URL).content.decode()
    assert "Horário de funcionamento salvo." in tela
    assert 'value="08:00"' in tela


def test_salvar_de_novo_atualiza_sem_duplicar(logado):
    logado.post(URL, semana())
    logado.post(URL, semana(d0_abertura="10:00"))
    assert HorarioFuncionamento.objects.count() == 7
    assert HorarioFuncionamento.objects.get(dia_semana=0).abertura == time(10)


@pytest.mark.parametrize("fechamento", ["09:00", "08:30"])
def test_fechamento_antes_ou_igual_a_abertura(logado, fechamento):
    """Critério 2: fechamento anterior ou igual à abertura mostra erro e nada é gravado."""
    logado.post(URL, semana())
    resposta = logado.post(URL, semana(d0_abertura="09:00", d0_fechamento=fechamento, d1_abertura="07:00"))

    assert resposta.status_code == 200
    segunda = resposta.context["forms"][0]
    assert segunda.errors["fechamento"] == ["O fechamento precisa ser depois da abertura."]
    html = resposta.content.decode()
    assert "Nada foi salvo." in html
    assert 'aria-describedby="id_dia0-fechamento-erro"' in html
    # Nenhum dia mudou, nem o terça-feira, que estava válido no mesmo envio.
    assert HorarioFuncionamento.objects.get(dia_semana=1).abertura == time(9)


def test_dia_aberto_sem_horario(logado):
    resposta = logado.post(URL, semana(d2_abertura=""))
    assert resposta.context["forms"][2].errors["abertura"] == ["Obrigatório quando o dia está aberto."]
    assert not HorarioFuncionamento.objects.exists()


def test_horario_invalido(logado):
    resposta = logado.post(URL, semana(d3_abertura="25:99"))
    assert resposta.context["forms"][3].errors["abertura"] == ["Informe um horário, como 09:00."]


def test_dia_fechado_nao_tem_horarios(logado):
    """Critério 3: dia marcado como fechado não tem intervalo, então nenhum horário aparece (base do RF05)."""
    logado.post(URL, semana())

    assert HorarioFuncionamento.intervalo_do_dia(SEGUNDA) == (time(9), time(19))
    assert HorarioFuncionamento.intervalo_do_dia(DOMINGO) is None


def test_fechar_dia_descarta_os_horarios(logado):
    logado.post(URL, semana(d0_aberto=None))
    segunda = HorarioFuncionamento.objects.get(dia_semana=0)
    assert (segunda.aberto, segunda.abertura) == (False, None)
    assert HorarioFuncionamento.intervalo_do_dia(SEGUNDA) is None


def test_dia_sem_configuracao_conta_como_fechado():
    assert HorarioFuncionamento.intervalo_do_dia(SEGUNDA) is None


def test_mudar_horario_nao_mexe_em_outras_tabelas(logado):
    """Critério 4 (parte que já existe): salvar o horário só altera horario_funcionamento.

    A tabela de agendamentos chega com o RF06; lá este critério ganha o teste com agendamentos reais.
    """
    usuario = Usuario.objects.create_user(email="b@exemplo.com", password="x", nome="B", papel="barbeiro")
    servico = Servico.objects.create(
        barbeiro=Barbeiro.objects.create(usuario=usuario, especialidade="Corte"), nome="Corte", preco=40, duracao_min=30
    )
    logado.post(URL, semana())
    logado.post(URL, semana(d0_aberto=None))

    servico.refresh_from_db()
    assert servico.ativo
    assert Usuario.objects.count() == 2


@pytest.mark.parametrize("papel", ["cliente", "barbeiro"])
def test_so_admin_configura(cliente_https, papel):
    usuario = Usuario.objects.create_user(email="u@exemplo.com", password="x", nome="U", papel=papel)
    cliente_https.force_login(usuario)
    assert cliente_https.get(URL).status_code == 403
    assert cliente_https.post(URL, semana()).status_code == 403
    assert not HorarioFuncionamento.objects.exists()


def test_visitante_vai_para_login(cliente_https):
    resposta = cliente_https.get(URL)
    assert resposta.status_code == 302
    assert resposta.url.startswith(reverse("entrar"))


def test_usuario_com_papel_admin_sem_superusuario(cliente_https):
    admin = Usuario.objects.create_user(email="gp@exemplo.com", password="x", nome="GP", papel="admin")
    cliente_https.force_login(admin)
    assert cliente_https.get(URL).status_code == 200
    assert URL in cliente_https.get(reverse("home")).content.decode()


def test_banco_recusa_fechamento_antes_da_abertura():
    with pytest.raises(IntegrityError), transaction.atomic():
        HorarioFuncionamento.objects.create(dia_semana=0, aberto=True, abertura=time(10), fechamento=time(9))


def test_banco_recusa_dia_repetido():
    HorarioFuncionamento.objects.create(dia_semana=0)
    with pytest.raises(IntegrityError), transaction.atomic():
        HorarioFuncionamento.objects.create(dia_semana=0)


def test_clean_do_modelo():
    from django.core.exceptions import ValidationError

    with pytest.raises(ValidationError):
        HorarioFuncionamento(dia_semana=0, aberto=True, abertura=time(10), fechamento=time(9)).clean()
    with pytest.raises(ValidationError):
        HorarioFuncionamento(dia_semana=0, aberto=True).clean()
    HorarioFuncionamento(dia_semana=0, aberto=False).clean()


def test_str():
    assert str(HorarioFuncionamento(dia_semana=6)) == "Domingo: fechado"
    dia = HorarioFuncionamento(dia_semana=0, aberto=True, abertura=time(9), fechamento=time(18, 30))
    assert str(dia) == "Segunda-feira: 09:00–18:30"
