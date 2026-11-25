from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction

from .models import Barbeiro, Usuario


class CadastroForm(forms.ModelForm):
    """Base dos cadastros: nome, e-mail único e senha validada, gravada só como hash."""

    papel = None

    senha = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Pelo menos 8 caracteres.",
    )

    class Meta:
        model = Usuario
        fields = ["nome", "email"]
        widgets = {
            "nome": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }
        error_messages = {
            "email": {"unique": "E-mail já cadastrado.", "invalid": "Informe um e-mail válido."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.error_messages["required"] = "Este campo é obrigatório."

    def clean_email(self):
        email = Usuario.objects.normalize_email(self.cleaned_data["email"]).lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("E-mail já cadastrado.", code="unique")
        return email

    def _post_clean(self):
        super()._post_clean()
        senha = self.cleaned_data.get("senha")
        if senha:
            try:
                password_validation.validate_password(senha, self.instance)
            except forms.ValidationError as erro:
                self.add_error("senha", erro)

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.papel = self.papel
        usuario.set_password(self.cleaned_data["senha"])
        if commit:
            usuario.save()
        return usuario


class CadastroClienteForm(CadastroForm):
    """RF01: cadastro de cliente com nome, e-mail e senha."""

    papel = Usuario.Papel.CLIENTE


class CadastroBarbeiroForm(CadastroForm):
    """RF04: cadastro de barbeiro com nome, e-mail, senha e especialidade."""

    papel = Usuario.Papel.BARBEIRO

    especialidade = forms.CharField(
        label="Especialidade",
        max_length=120,
        help_text="Ex.: cortes clássicos, degradê, barba.",
    )
    field_order = ["nome", "email", "especialidade", "senha"]

    def clean_especialidade(self):
        especialidade = self.cleaned_data["especialidade"].strip()
        if not especialidade:
            raise forms.ValidationError("Este campo é obrigatório.", code="required")
        return especialidade

    def save(self, commit=True):
        if not commit:
            raise ValueError("O cadastro de barbeiro grava usuário e perfil juntos: use commit=True.")
        with transaction.atomic():
            usuario = super().save(commit=True)
            Barbeiro.objects.create(usuario=usuario, especialidade=self.cleaned_data["especialidade"])
        return usuario


class LoginForm(AuthenticationForm):
    """RF02/RF03: login por e-mail e senha, com a mesma mensagem para qualquer erro."""

    error_messages = {
        "invalid_login": "E-mail ou senha inválidos.",
        "inactive": "E-mail ou senha inválidos.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "E-mail"
        self.fields["username"].widget = forms.EmailInput(attrs={"autocomplete": "email", "autofocus": True})
        self.fields["password"].label = "Senha"
        for campo in self.fields.values():
            campo.error_messages["required"] = "Este campo é obrigatório."

    def clean_username(self):
        # O cadastro grava o e-mail em minúsculas (RF01); o login aceita qualquer caixa.
        return self.cleaned_data["username"].strip().lower()
