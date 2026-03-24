from django.urls import include, path

urlpatterns = [
    path("v1/", include("schoolar_s.api.v1.urls")),
    path("v2/", include("schoolar_s.api.v2.urls")),
    path("v3/", include("schoolar_s.api.v3.urls")),
]
