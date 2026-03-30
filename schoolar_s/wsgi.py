"""
WSGI config do projeto schoolar_s.

Expõe a callable WSGI como variável de módulo ``application``.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schoolar_s.settings")

application = get_wsgi_application()
