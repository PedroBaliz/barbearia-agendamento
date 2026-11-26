from django import forms

ERRO_FECHAMENTO = "O fechamento precisa ser depois da abertura."
ERRO_OBRIGATORIO = "Obrigatório quando o dia está aberto."


class DiaFuncionamentoForm(forms.Form):
    """RF18: um dia da semana: aberto ou fechado e, se aberto, abertura e fechamento."""

    aberto = forms.BooleanField(label="Aberto", required=False)
    abertura = forms.TimeField(
        label="Abertura", required=False, widget=forms.TimeInput(attrs={"type": "time"}, format="%H:%M")
    )
    fechamento = forms.TimeField(
        label="Fechamento", required=False, widget=forms.TimeInput(attrs={"type": "time"}, format="%H:%M")
    )

    def __init__(self, *args, dia, nome_dia, **kwargs):
        super().__init__(*args, **kwargs)
        self.dia = dia
        self.nome_dia = nome_dia
        for campo in ("abertura", "fechamento"):
            self.fields[campo].error_messages["invalid"] = "Informe um horário, como 09:00."

    def clean(self):
        dados = super().clean()
        if not dados.get("aberto"):
            # Dia fechado não guarda horário: evita lixo e mantém a constraint do banco simples.
            dados["abertura"] = dados["fechamento"] = None
            return dados
        abertura, fechamento = dados.get("abertura"), dados.get("fechamento")
        for campo, valor in (("abertura", abertura), ("fechamento", fechamento)):
            if valor is None and campo not in self.errors:
                self.add_error(campo, ERRO_OBRIGATORIO)
        if abertura and fechamento and fechamento <= abertura:
            self.add_error("fechamento", ERRO_FECHAMENTO)
        return dados
