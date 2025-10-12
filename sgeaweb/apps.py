# Configuração do app principal do projeto (sgeaweb)

from django.apps import AppConfig

class SgeawebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sgeaweb'
    verbose_name = "SGEA (aplicativo principal)"  # aparece no /admin
