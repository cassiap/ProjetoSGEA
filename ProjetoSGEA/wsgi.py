# O WSGI é a interface usada pelos servidores web para se comunicar com aplicações Django.

import os
from django.core.wsgi import get_wsgi_application

# Define o módulo de configurações padrão do projeto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProjetoSGEA.settings')

# Cria a aplicação WSGI que será utilizada pelo servidor web
application = get_wsgi_application()
