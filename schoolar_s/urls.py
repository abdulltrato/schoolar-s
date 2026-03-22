"""
URL configuration for schoolar_s project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include([
        path("academico/", include("academico.urls")),
        path("curriculo/", include("curriculo.urls")),
        path("avaliacao/", include("avaliacao.urls")),
        path("progresso/", include("progresso.urls")),
        path("escola/", include("escola.urls")),
        path("relatorios/", include("relatorios.urls")),
        path("eventos/", include("eventos.urls")),
    ])),
]
