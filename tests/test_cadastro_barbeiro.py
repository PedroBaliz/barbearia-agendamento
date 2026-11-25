"""RF04 – Como barbeiro, quero me cadastrar informando nome e especialidade (issue #4)."""

import pytest
from django.urls import reverse

from contas.forms import CadastroBarbeiroForm
from contas.models import Barbeiro, Usuario

URL = reverse("cadastro_barbeiro")
DADOS = {
    "nome": "Bruno Lima",
    "email": "bruno@exemplo.com",
    "especialidade": "Degradê e barba",
    "senha": "navalha-afiada-7",
}

pytestmark = pytest.mark.django_db


def test_cadastro_barbeiro(cliente_https):
    """Critério 1: cria usuário com papel barbeiro e o perfil de barbeiro ligado a ele."""
    resposta = cliente_https.post(URL, DADOS)

    assert resposta.status_code == 302
    usuario = Usuario.objects.get(email="bruno@exemplo.com")
    assert usuario.papel == Usuario.Papel.BARBEIRO
    assert usuario.check_password(DADOS["senha"])
    assert usuario.barbeiro.especialidade == "Degradê e barba"
    assert usuario.barbeiro.ativo
    assert int(cliente_https.session["_auth_user_id"]) == usuario.pk


def test_tela_de_cadastro_barbeiro_abre(cliente_https):
    resposta = cliente_https.get(URL)
    assert resposta.status_code == 200
    assert list(resposta.context["form"].fields) == ["nome", "email", "especialidade", "senha"]


@pytest.mark.parametrize("especialidade", ["", "   "])
def test_especialidade_em_branco(cliente_https, especialidade):
    """Critério 2: sem especialidade o cadastro não conclui e o campo fica destacado."""
    resposta = cliente_https.post(URL, {**DADOS, "especialidade": especialidade})

    assert resposta.status_code == 200
    assert resposta.context["form"].errors["especialidade"] == ["Este campo é obrigatório."]
    assert 'id="id_especialidade"' in resposta.content.decode()
    assert "is-invalid" in resposta.content.decode()
    assert not Usuario.objects.exists()
    assert not Barbeiro.objects.exists()


def test_email_ja_cadastrado(cliente_https):
    """Critério 3: e-mail existente mostra "E-mail já cadastrado" (vale também para e-mail de cliente)."""
    Usuario.objects.create_user(email="bruno@exemplo.com", password="outra-senha-123", nome="Cliente")

    resposta = cliente_https.post(URL, {**DADOS, "email": "Bruno@Exemplo.com"})

    assert "E-mail já cadastrado" in resposta.content.decode()
    assert Usuario.objects.count() == 1
    assert not Barbeiro.objects.exists()


def test_barbeiro_aparece_entre_os_disponiveis(cliente_https):
    """Critério 4: depois do cadastro, o barbeiro está na lista de disponíveis para agendamento."""
    cliente_https.post(URL, DADOS)

    disponiveis = Barbeiro.objects.disponiveis()
    assert [b.usuario.email for b in disponiveis] == ["bruno@exemplo.com"]


def test_disponiveis_exclui_inativos():
    for i, (perfil_ativo, conta_ativa) in enumerate([(True, True), (False, True), (True, False)]):
        usuario = Usuario.objects.create_user(
            email=f"b{i}@exemplo.com", password="x", nome=f"B{i}", papel="barbeiro", is_active=conta_ativa
        )
        Barbeiro.objects.create(usuario=usuario, especialidade="Corte", ativo=perfil_ativo)

    assert [b.usuario.email for b in Barbeiro.objects.disponiveis()] == ["b0@exemplo.com"]


def test_falha_no_perfil_nao_deixa_usuario_orfao(monkeypatch):
    """Usuário e perfil são gravados na mesma transação."""
    form = CadastroBarbeiroForm(DADOS)
    assert form.is_valid()

    def falhar(**_):
        raise RuntimeError("banco caiu")

    monkeypatch.setattr(Barbeiro.objects, "create", falhar)
    with pytest.raises(RuntimeError):
        form.save()
    assert not Usuario.objects.exists()


def test_save_sem_commit_recusado():
    form = CadastroBarbeiroForm(DADOS)
    assert form.is_valid()
    with pytest.raises(ValueError):
        form.save(commit=False)


def test_str_do_barbeiro():
    usuario = Usuario.objects.create_user(email="c@exemplo.com", password="x", nome="Caio", papel="barbeiro")
    assert str(Barbeiro.objects.create(usuario=usuario, especialidade="Navalha")) == "Caio (Navalha)"


def test_cadastro_de_cliente_continua_cliente(cliente_https):
    cliente_https.post(reverse("cadastro"), {k: v for k, v in DADOS.items() if k != "especialidade"})
    usuario = Usuario.objects.get()
    assert usuario.papel == Usuario.Papel.CLIENTE
    assert not Barbeiro.objects.exists()
