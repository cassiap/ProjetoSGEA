# sgeaweb/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    # Auth
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("cadastro/", views.cadastro_view, name="cadastro"),
    # Confirmação de e-mail
    path("confirmar/<str:token>/", views.confirmar_email, name="confirmar_email"),
    # Eventos
    path("eventos/", views.evento_list, name="evento_list"),
    path("eventos/novo/", views.evento_create, name="evento_create"),
    path("eventos/<int:pk>/editar/", views.evento_update, name="evento_update"),
    path("eventos/<int:pk>/deletar/", views.evento_delete, name="evento_delete"),
    path("eventos/<int:pk>/inscricoes/", views.evento_inscricoes, name="evento_inscricoes"),
    path("eventos/<int:pk>/detalhes/", views.evento_detalhe, name="evento_detalhe"),
    # Inscrições
    path("inscrever/<int:pk_evento>/", views.inscrever, name="inscrever"),
    path("minhas-inscricoes/", views.minhas_inscricoes, name="minhas_inscricoes"),
    # Certificados
    path("certificados/emitir/<int:pk_inscricao>/", views.emitir_certificado, name="emitir_certificado"),
    path("certificados/<int:pk_inscricao>/", views.certificado_detalhe, name="certificado_detalhe"),
    path("certificados/<int:pk_inscricao>/pdf/", views.certificado_pdf, name="certificado_pdf"),
]
