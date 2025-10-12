# Arquivo de configurações principais do projeto Django (SGEA)
# Ajustado para ambiente de desenvolvimento local

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Chave usada pelo Django para criptografia interna (sem necessidade de troca em ambiente de teste)
SECRET_KEY = 'dev-not-secret'

# Modo de depuração ativado (apenas durante o desenvolvimento)
DEBUG = True

# Hosts permitidos para execução local
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Aplicações ativas no projeto
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sgeaweb.apps.SgeawebConfig',  # aplicativo principal do sistema
]

# Middlewares responsáveis por processar as requisições HTTP
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Arquivo principal de rotas do projeto
ROOT_URLCONF = 'ProjetoSGEA.urls'

# Configurações de templates HTML
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # os templates estão organizados dentro do app "sgeaweb"
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Configuração da aplicação WSGI (padrão do Django)
WSGI_APPLICATION = 'ProjetoSGEA.wsgi.application'

# Banco de dados SQLite (ideal para desenvolvimento)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Validação de senha desativada para facilitar testes locais
AUTH_PASSWORD_VALIDATORS = []

# Idioma e fuso horário do projeto
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Configuração dos arquivos estáticos (CSS, JS, imagens)
STATIC_URL = 'static/'

# Chave padrão para campos automáticos do Django
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Rotas padrão de autenticação
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
