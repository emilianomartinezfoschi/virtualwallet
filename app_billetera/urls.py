from django.urls import path
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
# from django.conf import settings

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("perfil/<str:name>", views.perfil, name="perfil"),
    path("cambio/<str:name>", views.cambio, name="cambio"),
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),
    ),
]
