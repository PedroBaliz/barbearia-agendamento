from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render


def home(request):
    return render(request, "core/home.html")


def saude(request):
    """Healthcheck do deploy: responde 200 se a aplicação e o banco estão de pé."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        banco = "ok"
        status = 200
    except Exception:  # noqa: BLE001 - qualquer falha de banco deixa o serviço indisponível
        banco = "erro"
        status = 503
    return JsonResponse({"status": "ok" if status == 200 else "erro", "banco": banco}, status=status)
