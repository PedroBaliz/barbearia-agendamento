from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UsuarioManager(BaseUserManager):
    """Cria usuários identificados pelo e-mail, não por username."""

    use_in_migrations = True

    def _criar(self, email, password, **campos):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        usuario = self.model(email=self.normalize_email(email), **campos)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **campos):
        campos.setdefault("is_staff", False)
        campos.setdefault("is_superuser", False)
        return self._criar(email, password, **campos)

    def create_superuser(self, email, password=None, **campos):
        campos.setdefault("is_staff", True)
        campos.setdefault("is_superuser", True)
        campos.setdefault("papel", Usuario.Papel.ADMIN)
        if not campos["is_staff"] or not campos["is_superuser"]:
            raise ValueError("Superusuário precisa de is_staff=True e is_superuser=True.")
        return self._criar(email, password, **campos)


class Usuario(AbstractUser):
    """Tabela `usuario` do modelo de dados (docs/modelo-de-dados.md)."""

    class Papel(models.TextChoices):
        CLIENTE = "cliente", "Cliente"
        BARBEIRO = "barbeiro", "Barbeiro"
        ADMIN = "admin", "Admin"

    username = None
    first_name = None
    last_name = None

    nome = models.CharField(max_length=120)
    email = models.EmailField("e-mail", unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    papel = models.CharField(max_length=10, choices=Papel.choices, default=Papel.CLIENTE)
    criado_em = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    objects = UsuarioManager()

    class Meta:
        db_table = "usuario"
        verbose_name = "usuário"
        verbose_name_plural = "usuários"

    def __str__(self):
        return f"{self.nome} <{self.email}>"
