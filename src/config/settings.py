"""Configurações do Django para o Barbearia Agendamento.

Tudo que muda entre ambientes vem de variáveis de ambiente (ver .env.example na raiz).
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # src/
load_dotenv(BASE_DIR.parent / ".env")


def env_bool(nome: str, padrao: bool = False) -> bool:
    return os.getenv(nome, str(padrao)).strip().lower() in {"1", "true", "yes", "sim"}


def env_list(nome: str, padrao: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(nome, padrao).split(",") if item.strip()]


DEBUG = env_bool("DEBUG", False)

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise RuntimeError("Defina SECRET_KEY no ambiente (veja .env.example).")
    SECRET_KEY = "dev-inseguro-apenas-local"

# A Vercel define VERCEL=1 em todo deploy (produção e preview).
NA_VERCEL = bool(os.getenv("VERCEL"))

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
if NA_VERCEL:
    ALLOWED_HOSTS.append(".vercel.app")
    CSRF_TRUSTED_ORIGINS.append("https://*.vercel.app")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "contas",
    "core",
    "servicos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Banco: DATABASE_URL (PostgreSQL da Vercel/Neon); sem ela, SQLite local.
# `or` trata DATABASE_URL vazia (como no .env.example) igual a ausente.
DATABASE_URL = os.getenv("DATABASE_URL") or ""
if NA_VERCEL and not DATABASE_URL:
    # O disco da Vercel é temporário: SQLite perderia os dados a cada requisição.
    raise RuntimeError("Na Vercel, conecte um PostgreSQL (Storage → Neon) para definir DATABASE_URL.")
DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL or f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        # Serverless: sem conexões persistentes entre invocações.
        conn_max_age=0 if NA_VERCEL else 600,
        conn_health_checks=True,
    )
}

# Usuário customizado com login por e-mail (modelo de dados: tabela usuario).
AUTH_USER_MODEL = "contas.Usuario"
LOGIN_URL = "entrar"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# RNF02: senhas com hash bcrypt.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
# Sem etapa de collectstatic na Vercel: o WhiteNoise serve direto das pastas static dos apps.
WHITENOISE_USE_FINDERS = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Atrás do proxy HTTPS da Vercel.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    # Monitores de disponibilidade podem chamar /saude/ por HTTP: não redirecionar.
    SECURE_REDIRECT_EXEMPT = [r"^saude/$"]
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # HSTS desligado de propósito: só ativar com domínio próprio e HTTPS estável (difícil de reverter).
