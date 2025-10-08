# Arquivo responsável por mapear as rotas principais do projeto Django (SGEA)
# Aqui fazemos a ligação entre o sistema administrativo e as rotas do aplicativo principal (sgeaweb)

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Rota para acessar o painel administrativo do Django
    path('admin/', admin.site.urls),

    # Inclui todas as rotas definidas dentro do aplicativo "sgeaweb"
    # Assim, qualquer URL começando por "/" será redirecionada para as rotas do app
    path('', include('sgeaweb.urls')),
]
