# Rotas do aplicativo principal (sgeaweb)
# Aqui ficam as URLs que apontam para as views de home, autenticação, eventos, inscrições e certificados.
from django.urls import path
from . import views

urlpatterns = [
    # Home (lista de eventos abertos)
    path("", views.home, name="home"),

    # Autenticação / Usuário
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("cadastro/", views.cadastro_view, name="cadastro"),

    # Eventos (acesso do ORGANIZADOR)
    path("eventos/", views.evento_list, name="evento_list"),
    path("eventos/novo/", views.evento_create, name="evento_create"),
    path("eventos/<int:pk>/editar/", views.evento_update, name="evento_update"),
    path("eventos/<int:pk>/deletar/", views.evento_delete, name="evento_delete"),

    # Inscrições (aluno/professor)
    path("inscrever/<int:pk_evento>/", views.inscrever, name="inscrever"),
    path("minhas-inscricoes/", views.minhas_inscricoes, name="minhas_inscricoes"),

    # Certificados (organizador emite)
    path("certificados/emitir/<int:pk_inscricao>/", views.emitir_certificado, name="emitir_certificado"),
]
