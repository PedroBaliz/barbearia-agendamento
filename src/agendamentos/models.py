from django.core.exceptions import ValidationError
from django.db import models


class HorarioFuncionamento(models.Model):
    """Tabela `horario_funcionamento` do modelo de dados: um registro por dia da semana (RF18)."""

    class DiaSemana(models.IntegerChoices):
        SEGUNDA = 0, "Segunda-feira"
        TERCA = 1, "Terça-feira"
        QUARTA = 2, "Quarta-feira"
        QUINTA = 3, "Quinta-feira"
        SEXTA = 4, "Sexta-feira"
        SABADO = 5, "Sábado"
        DOMINGO = 6, "Domingo"

    dia_semana = models.PositiveSmallIntegerField("dia da semana", choices=DiaSemana.choices, unique=True)
    aberto = models.BooleanField(default=False)
    abertura = models.TimeField(null=True, blank=True)
    fechamento = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "horario_funcionamento"
        ordering = ["dia_semana"]
        verbose_name = "horário de funcionamento"
        verbose_name_plural = "horários de funcionamento"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(aberto=False)
                | models.Q(abertura__isnull=False, fechamento__isnull=False, fechamento__gt=models.F("abertura")),
                name="horario_aberto_com_fechamento_depois_da_abertura",
            ),
        ]

    def __str__(self):
        if not self.aberto:
            return f"{self.get_dia_semana_display()}: fechado"
        return f"{self.get_dia_semana_display()}: {self.abertura:%H:%M}–{self.fechamento:%H:%M}"

    def clean(self):
        if self.aberto:
            if not self.abertura or not self.fechamento:
                raise ValidationError("Informe a abertura e o fechamento do dia aberto.")
            if self.fechamento <= self.abertura:
                raise ValidationError({"fechamento": "O fechamento precisa ser depois da abertura."})

    @classmethod
    def intervalo_do_dia(cls, data):
        """(abertura, fechamento) da data, ou None se a barbearia não abre nesse dia.

        Dia sem configuração conta como fechado. É a base do cálculo de horários livres (RF05).
        """
        dia = cls.objects.filter(dia_semana=data.weekday(), aberto=True).first()
        return (dia.abertura, dia.fechamento) if dia else None
