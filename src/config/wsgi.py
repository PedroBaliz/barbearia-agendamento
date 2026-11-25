"""Configuração WSGI: expõe ``application`` para o servidor (Vercel ou outro).

A Vercel detecta o Django e carrega este arquivo direto, a partir da raiz do
repositório. Por isso a pasta src/ é colocada no caminho de importação aqui,
para que ``config``, ``contas`` e ``core`` sejam encontrados.
"""

import os
import sys
from pathlib import Path

PASTA_SRC = str(Path(__file__).resolve().parent.parent)
if PASTA_SRC not in sys.path:
    sys.path.insert(0, PASTA_SRC)

from django.core.wsgi import get_wsgi_application  # noqa: E402

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
app = application  # nome que o runtime Python da Vercel também procura
