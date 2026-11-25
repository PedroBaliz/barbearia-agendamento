"""Entrada da Vercel: expõe o Django (WSGI) como função serverless Python."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from config.wsgi import application  # noqa: E402

app = application
