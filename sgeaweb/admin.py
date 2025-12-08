# sgeaweb/admin.py
from django.contrib import admin
from .models import TipoEvento, PerfilUsuario, Evento, Inscricao, Certificado, Auditoria

@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "data_criacao", "data_atualizacao")
    search_fields = ("nome",)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "perfil", "instituicao", "email_confirmado")
    list_filter = ("perfil", "email_confirmado")
    search_fields = ("user__username", "user__email", "instituicao")

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "TIPO", "data_inicio", "data_fim", "organizador", "responsavel")
    list_filter = ("TIPO", "data_inicio", "data_fim")
    search_fields = ("titulo", "local")
    autocomplete_fields = ("organizador", "responsavel")

@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ("id", "participante", "evento", "presenca_confirmada", "criado_em")
    list_filter = ("presenca_confirmada", "criado_em")
    search_fields = ("participante__username", "evento__titulo")

@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    list_display = ("inscricao", "codigo_validacao", "emitido_em")
    search_fields = ("codigo_validacao", "inscricao__participante__username")

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "acao", "data_hora")
    list_filter = ("acao", "data_hora")
    search_fields = ("usuario__username", "acao", "descricao")
