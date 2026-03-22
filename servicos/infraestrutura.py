from django.core.cache import cache
from django.db import connection


def verificar_banco():
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return "ok"


def verificar_cache():
    cache.set("readiness-check", "ok", 5)
    return "ok" if cache.get("readiness-check") == "ok" else "error"
