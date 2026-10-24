from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic.base import RedirectView

from . import views
from .forms import LoginForm

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("perfil/<str:name>", views.perfil, name="perfil"),
    path("cambio/<str:name>", views.cambio, name="cambio"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            authentication_form=LoginForm, redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/favicon.ico"),
    ),
]