from django import forms
from django.contrib.auth import password_validation

from .models import Usuario


class CadastroClienteForm(forms.ModelForm):
    """RF01: cadastro de cliente com nome, e-mail e senha."""

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
        usuario.papel = Usuario.Papel.CLIENTE
        usuario.set_password(self.cleaned_data["senha"])
        if commit:
            usuario.save()
        return usuario
