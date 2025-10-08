from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("cadastro/", views.cadastro_view, name="cadastro"),

    path("eventos/", views.evento_list, name="evento_list"),
    path("eventos/novo/", views.evento_create, name="evento_create"),
    path("eventos/<int:pk>/editar/", views.evento_update, name="evento_update"),
    path("eventos/<int:pk>/deletar/", views.evento_delete, name="evento_delete"),

    path("inscrever/<int:pk_evento>/", views.inscrever, name="inscrever"),
    path("minhas-inscricoes/", views.minhas_inscricoes, name="minhas_inscricoes"),

    path("certificados/emitir/<int:pk_inscricao>/", views.emitir_certificado, name="emitir_certificado"),
]
