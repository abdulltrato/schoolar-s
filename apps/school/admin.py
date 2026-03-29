from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

# Import admin registrations (executing these modules registers the models)
from . import admin_simple  # noqa: F401
from . import admin_classroom  # noqa: F401
from . import admin_enrollment  # noqa: F401
from . import admin_user  # noqa: F401

admin.site.unregister(Group)
admin.site.unregister(get_user_model())
