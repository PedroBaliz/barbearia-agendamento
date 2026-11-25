import pytest


@pytest.fixture
def cliente_web(client):
    """Cliente HTTP do Django (atalho com nome em português)."""
    return client
