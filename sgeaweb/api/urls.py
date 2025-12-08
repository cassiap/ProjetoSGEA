from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("auth/token/", views.ObtainAuthTokenBrowsable.as_view(), name="api_auth_token"),
    path("eventos/", views.EventoListAPI.as_view(), name="api_eventos"),
    path("inscricoes/", views.InscricaoCreateAPI.as_view(), name="api_inscricoes"),
]


urlpatterns = [
    # rotas
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
