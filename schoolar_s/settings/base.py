import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-secret-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"

default_allowed_hosts = ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]
configured_allowed_hosts = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", ",".join(default_allowed_hosts)).split(",")
    if host.strip()
]
ALLOWED_HOSTS = list(dict.fromkeys(configured_allowed_hosts + default_allowed_hosts))


# Application definition

SHARED_APPS = [
    # "django_tenants",  # mandatory
    # "tenants",  # you must list the app where your tenant model resides in

    "jazzmin",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "corsheaders",
]

TENANT_APPS = [
    # your tenant-specific apps
    "apps.academic",
    "apps.curriculum",
    "apps.assessment",
    "apps.learning",
    "apps.progress",
    "apps.school",
    "apps.reports",
    "apps.events",
]

INSTALLED_APPS = SHARED_APPS + TENANT_APPS  # list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

# TENANT_MODEL = "tenants.School"  # app.Model

# TENANT_DOMAIN_MODEL = "tenants.Domain"  # app.Model

MIDDLEWARE = [
    # "django_tenants.middleware.main.TenantMainMiddleware",  # mandatory
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "core.middleware.RequestContextMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.ResponseHeadersMiddleware",
]

# DATABASE_ROUTERS = (
#     "django_tenants.routers.TenantSyncRouter",
# )

ROOT_URLCONF = "schoolar_s.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "builtins": [
                "core.templatetags.compat_filters",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "schoolar_s.wsgi.application"


def env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


USE_POSTGRES = env_bool("USE_POSTGRES", False)
REQUIRE_USER_PROFILE = env_bool("REQUIRE_USER_PROFILE", True)
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", not DEBUG)
SESSION_COOKIE_HTTPONLY = env_bool("SESSION_COOKIE_HTTPONLY", True)
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
SESSION_COOKIE_AGE = int(os.getenv("SESSION_COOKIE_AGE", str(60 * 60 * 8)))
SESSION_SAVE_EVERY_REQUEST = env_bool("SESSION_SAVE_EVERY_REQUEST", True)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_HTTPONLY = env_bool("CSRF_COOKIE_HTTPONLY", False)
CSRF_COOKIE_SAMESITE = os.getenv("CSRF_COOKIE_SAMESITE", "Lax")
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if USE_POSTGRES:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "schoolar"),
            "USER": os.getenv("POSTGRES_USER", "schoolar"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "schoolar"),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "Africa/Maputo")

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# The domain apps were renamed to English identifiers. Keeping the legacy
# migrations in sync would require a full migration tree rewrite, so these
# apps are created directly from the current models.
MIGRATION_MODULES = {
    "academic": None,
    "assessment": None,
    "curriculum": None,
    "events": None,
    "learning": None,
    "progress": None,
    "reports": None,
    "school": None,
    "tenants": None,
}

# DRF settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/minute",
        "user": "300/minute",
    },
    "EXCEPTION_HANDLER": "core.api.custom_exception_handler",
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "schoolar-s-local-cache",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "loggers": {
        "schoolar.request": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "schoolar.api": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "schoolar.audit": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

# Jazzmin settings for modern admin theme
JAZZMIN_SETTINGS = {
    "site_title": "SUBSTRATO EDUCATION Admin",
    "site_header": "SUBSTRATO EDUCATION",
    "site_brand": "Schoolar-S",
    "site_logo": None,
    "login_logo": None,
    "login_logo_dark": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "Welcome to SUBSTRATO EDUCATION",
    "copyright": "SUBSTRATO EDUCATION Ltd",
    "search_model": ["academic.Student", "curriculum.Competency"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "academic.Student"},
        {"app": "curriculum"},
    ],
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"}
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["academic", "curriculum", "assessment", "progress", "school", "reports", "events"],
    "custom_links": {},
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "academic.Student": "fas fa-user-graduate",
        "academic.StudentCompetency": "fas fa-chart-line",
        "curriculum.CurriculumArea": "fas fa-book",
        "curriculum.Subject": "fas fa-chalkboard-teacher",
        "curriculum.Competency": "fas fa-target",
        "curriculum.BaseCurriculum": "fas fa-file-alt",
        "curriculum.LocalCurriculum": "fas fa-map-marker-alt",
        "assessment.Assessment": "fas fa-clipboard-check",
        "progress.Progression": "fas fa-arrow-up",
        "school.Teacher": "fas fa-user-tie",
        "school.Classroom": "fas fa-users",
        "school.Enrollment": "fas fa-user-plus",
        "reports.Report": "fas fa-chart-bar",
        "events.Event": "fas fa-calendar-alt",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
}

# Monkey patch for Django Context.__copy__ to fix Python 3.14 compatibility
from django.template.context import Context

def patched_copy(self):
    duplicate = Context(self.dicts)
    return duplicate

Context.__copy__ = patched_copy
