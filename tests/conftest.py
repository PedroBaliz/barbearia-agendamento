import pytest
from django.test import Client


@pytest.fixture
def cliente_web(client):
    """Cliente HTTP do Django (atalho com nome em português)."""
    return client


@pytest.fixture
def cliente_https():
    """Cliente sempre em HTTPS, como em produção atrás da Vercel (no CI, DEBUG=False liga o SECURE_SSL_REDIRECT)."""
    return Client(HTTP_X_FORWARDED_PROTO="https", **{"wsgi.url_scheme": "https"})
