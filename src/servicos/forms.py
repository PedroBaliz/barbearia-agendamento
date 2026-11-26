from django import forms

from .models import DURACAO_MAX, DURACAO_MIN, Servico


class ServicoForm(forms.ModelForm):
    """RF12: nome, descrição, preço e duração do serviço."""

    class Meta:
        model = Servico
        fields = ["nome", "descricao", "preco", "duracao_min"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "preco": forms.NumberInput(attrs={"step": "0.01", "min": "0.01", "inputmode": "decimal"}),
            "duracao_min": forms.NumberInput(attrs={"step": "5", "min": DURACAO_MIN, "max": DURACAO_MAX}),
        }
        help_texts = {"duracao_min": f"Entre {DURACAO_MIN} e {DURACAO_MAX} minutos."}
        error_messages = {
            "preco": {
                "min_value": "O preço precisa ser maior que zero.",
                "invalid": "Informe um valor em reais, como 35,00.",
                "max_digits": "Valor alto demais.",
            },
            "duracao_min": {
                "min_value": f"A duração mínima é {DURACAO_MIN} minutos.",
                "max_value": f"A duração máxima é {DURACAO_MAX} minutos.",
                "invalid": "Informe a duração em minutos.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.error_messages["required"] = "Este campo é obrigatório."
