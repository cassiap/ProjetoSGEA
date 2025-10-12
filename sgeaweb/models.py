# Modelos do SGEA (Sistema de Gestão de Eventos Acadêmicos)

from django.db import models
from django.contrib.auth.models import User


class TipoEvento(models.Model):
    """Tabela de tipos (palestra, minicurso, workshop etc.)."""
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tipo_evento"
        ordering = ["nome"]
        verbose_name = "Tipo de Evento"
        verbose_name_plural = "Tipos de Evento"

    def __str__(self):
        return self.nome


class PerfilUsuario(models.Model):
    """Dados complementares do usuário do Django (perfil e instituição)."""
    PERFIS = (
        ("ALUNO", "Aluno"),
        ("PROFESSOR", "Professor"),
        ("ORGANIZADOR", "Organizador"),
    )
    # related_name="perfil" permite acessar como user.perfil no projeto
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    telefone = models.CharField(max_length=20, blank=True)
    instituicao = models.CharField(max_length=150)
    perfil = models.CharField(max_length=12, choices=PERFIS)

    class Meta:
        db_table = "perfil_usuario"
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuário"

    def __str__(self):
        # Usa o nome completo se existir; senão, o username
        return f"{self.user.get_full_name() or self.user.username} - {self.perfil}"


class Evento(models.Model):
    """Evento acadêmico que pode receber inscrições."""
    TIPO = models.ForeignKey(TipoEvento, on_delete=models.PROTECT)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    horario = models.CharField(max_length=50)
    local = models.CharField(max_length=200)
    vagas = models.PositiveIntegerField()
    organizador = models.ForeignKey(User, on_delete=models.PROTECT, related_name="eventos")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "evento"
        ordering = ["-data_inicio", "titulo"]
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

    def __str__(self):
        return self.titulo


class Inscricao(models.Model):
    """Liga um participante a um evento (1 usuário pode se inscrever 1x por evento)."""
    participante = models.ForeignKey(User, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inscricao"
        unique_together = ("participante", "evento")  # evita duplicidade
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"

    def __str__(self):
        return f"{self.participante.username} → {self.evento.titulo}"


class Certificado(models.Model):
    """Certificado emitido para uma inscrição (1:1), com código de validação."""
    inscricao = models.OneToOneField(Inscricao, on_delete=models.CASCADE)
    emitido_em = models.DateTimeField(auto_now_add=True)
    codigo_validacao = models.CharField(max_length=64, unique=True)

    class Meta:
        db_table = "certificado"
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"

    def __str__(self):
        return f"Certificado {self.codigo_validacao}"
