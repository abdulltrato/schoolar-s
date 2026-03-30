from django.contrib import admin
# Administração padrão do Django.
from django.contrib.auth import get_user_model
# Utilitário para pegar o modelo de usuário custom.
from django.contrib.auth.models import Group
# Modelo de grupos do Django.

# Importar módulos registra os ModelAdmins declarados neles.
from . import admin_simple  # noqa: F401
from . import admin_classroom  # noqa: F401
from . import admin_enrollment  # noqa: F401
from . import admin_user  # noqa: F401

# Remove Group e User do admin, já que são geridos por telas customizadas.
admin.site.unregister(Group)
admin.site.unregister(get_user_model())
