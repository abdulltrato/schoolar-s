from django.core.cache import cache
from django.db import connection


def check_database():
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return "ok"


def check_cache():
    cache.set("readiness-check", "ok", 5)
    return "ok" if cache.get("readiness-check") == "ok" else "error"
