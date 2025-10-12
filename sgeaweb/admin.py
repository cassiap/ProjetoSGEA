# Configuração do painel administrativo do Django para o SGEA

from django.contrib import admin
from .models import TipoEvento, PerfilUsuario, Evento, Inscricao, Certificado

@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ("nome", "data_criacao", "data_atualizacao")
    search_fields = ("nome",)
    ordering = ("nome",)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "perfil", "instituicao", "telefone")
    list_filter = ("perfil",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "instituicao")
    raw_id_fields = ("user",)  # evita dropdown muito grande

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "TIPO", "data_inicio", "data_fim", "local", "vagas", "organizador")
    list_filter = ("TIPO", "data_inicio")
    search_fields = ("titulo", "local", "organizador__username")
    date_hierarchy = "data_inicio"
    raw_id_fields = ("organizador",)

@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ("participante", "evento", "criado_em")
    list_filter = ("evento",)
    search_fields = ("participante__username", "evento__titulo")
    raw_id_fields = ("participante", "evento")

@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    list_display = ("inscricao", "codigo_validacao", "emitido_em")
    search_fields = ("codigo_validacao", "inscricao__participante__username", "inscricao__evento__titulo")
