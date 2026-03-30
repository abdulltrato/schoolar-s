"""
ASGI config do projeto schoolar_s.

Expõe a callable ASGI como variável de módulo ``application``.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schoolar_s.settings")

application = get_asgi_application()
