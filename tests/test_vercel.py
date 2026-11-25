"""Configuração para a Vercel: testada em subprocessos, com as variáveis que a Vercel define."""

import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def rodar(codigo: str, **env_extra: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in {"DATABASE_URL", "VERCEL", "DEBUG"}}
    env.update({"SECRET_KEY": "chave-de-teste", "DEBUG": "false", "PYTHONPATH": str(RAIZ / "src"), **env_extra})
    return subprocess.run([sys.executable, "-c", codigo], cwd=RAIZ, env=env, capture_output=True, text=True)


def test_vercel_sem_banco_falha_com_mensagem_clara():
    """Na Vercel o disco é temporário: sem DATABASE_URL o app não deve subir com SQLite."""
    r = rodar("import config.settings", VERCEL="1", DATABASE_URL="")
    assert r.returncode != 0
    assert "DATABASE_URL" in r.stderr


def test_vercel_aceita_dominios_vercel_e_expoe_app_wsgi():
    codigo = (
        "import api.index as entrada; from django.conf import settings; "
        "assert callable(entrada.app); "
        "assert '.vercel.app' in settings.ALLOWED_HOSTS; "
        "assert 'https://*.vercel.app' in settings.CSRF_TRUSTED_ORIGINS; "
        "assert settings.DATABASES['default']['CONN_MAX_AGE'] == 0; "
        "print('ok')"
    )
    r = rodar(
        codigo, VERCEL="1", DATABASE_URL="postgresql://u:s@localhost:5432/db", DJANGO_SETTINGS_MODULE="config.settings"
    )
    assert r.returncode == 0, r.stderr
    assert "ok" in r.stdout
