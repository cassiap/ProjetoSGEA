from django.contrib import admin
from .models import TipoEvento, PerfilUsuario, Evento, Inscricao, Certificado

admin.site.register(TipoEvento)
admin.site.register(PerfilUsuario)
admin.site.register(Evento)
admin.site.register(Inscricao)
admin.site.register(Certificado)
