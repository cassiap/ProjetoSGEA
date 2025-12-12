from django.urls import path
from . import views

urlpatterns = [
    path("auth/token/", views.ObtainAuthTokenBrowsable.as_view(), name="api_auth_token"),
    path("eventos/", views.EventoListAPI.as_view(), name="api_eventos"),
    path("inscricoes/", views.InscricaoCreateAPI.as_view(), name="api_inscricoes"),
]
