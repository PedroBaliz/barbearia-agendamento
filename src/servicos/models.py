from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from contas.models import Barbeiro

DURACAO_MIN = 5
DURACAO_MAX = 480


class ServicoQuerySet(models.QuerySet):
    def disponiveis(self):
        """Serviços que o cliente pode ver e agendar: serviço, perfil do barbeiro e conta ativos."""
        return self.filter(ativo=True, barbeiro__ativo=True, barbeiro__usuario__is_active=True)


class Servico(models.Model):
    """Tabela `servico` do modelo de dados: cada barbeiro cadastra os seus (RF12)."""

    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.PROTECT, related_name="servicos")
    nome = models.CharField(max_length=100)
    descricao = models.TextField("descrição", blank=True)
    preco = models.DecimalField(
        "preço (R$)", max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    duracao_min = models.PositiveSmallIntegerField(
        "duração (min)", validators=[MinValueValidator(DURACAO_MIN), MaxValueValidator(DURACAO_MAX)]
    )
    ativo = models.BooleanField(default=True)

    objects = ServicoQuerySet.as_manager()

    class Meta:
        db_table = "servico"
        ordering = ["nome"]
        verbose_name = "serviço"
        verbose_name_plural = "serviços"
        constraints = [
            models.CheckConstraint(condition=models.Q(preco__gt=0), name="servico_preco_positivo"),
            models.CheckConstraint(
                condition=models.Q(duracao_min__gte=DURACAO_MIN, duracao_min__lte=DURACAO_MAX),
                name="servico_duracao_entre_5_e_480",
            ),
        ]

    def __str__(self):
        return f"{self.nome} – {self.barbeiro.usuario.nome}"

    @property
    def duracao_legivel(self):
        horas, minutos = divmod(self.duracao_min, 60)
        if not horas:
            return f"{minutos} min"
        return f"{horas}h{minutos:02d}" if minutos else f"{horas}h"
