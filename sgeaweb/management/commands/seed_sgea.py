
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from sgeaweb.models import PerfilUsuario, Evento, TipoEvento


class Command(BaseCommand):
    help = "Cria usuários iniciais para testes do SGEA (organizador, aluno e professor)."

    def handle(self, *args, **options):
        usuarios = [
            {
                "username": "organizador@sgea.com",
                "email": "organizador@sgea.com",
                "password": "Admin@123",
                "first_name": "Usuário",
                "last_name": "Organizador",
                "perfil": "ORGANIZADOR",
                "instituicao": "SGEA",
            },
            {
                "username": "aluno@sgea.com",
                "email": "aluno@sgea.com",
                "password": "Aluno@123",
                "first_name": "Usuário",
                "last_name": "Aluno",
                "perfil": "ALUNO",
                "instituicao": "SGEA",
            },
            {
                "username": "professor@sgea.com",
                "email": "professor@sgea.com",
                "password": "Professor@123",
                "first_name": "Usuário",
                "last_name": "Professor",
                "perfil": "PROFESSOR",
                "instituicao": "SGEA",
            },
        ]

        for dados in usuarios:
            username = dados["username"]
            email = dados["email"]
            password = dados["password"]
            first_name = dados["first_name"]
            last_name = dados["last_name"]
            perfil_tipo = dados["perfil"]
            instituicao = dados["instituicao"]

            #   CRIAÇÃO OU ATUALIZAÇÃO DO USER
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )

            # Se for criado agora, define a senha
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Usuário criado: {username} / senha: {password}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Usuário já existia: {username} (senha não alterada).")
                )

            #   CRIA OU ATUALIZA PERFIL
            perfil, perfil_created = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={
                    "telefone": "(61) 99999-9999",
                    "instituicao": instituicao,
                    "perfil": perfil_tipo,
                    "email_confirmado": True,   #marca como confirmado
                    "confirma_token": None,     #sem token necessário
                },
            )

            if perfil_created:
                self.stdout.write(
                    self.style.SUCCESS(f"Perfil criado para {username}: {perfil_tipo}")
                )
            else:
                # Atualiza caso esteja diferente ou sem confirmação
                mudou = False

                if perfil.perfil != perfil_tipo:
                    perfil.perfil = perfil_tipo
                    mudou = True

                if not perfil.email_confirmado:
                    perfil.email_confirmado = True
                    mudou = True

                if perfil.confirma_token is not None:
                    perfil.confirma_token = None
                    mudou = True

                if mudou:
                    perfil.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"Perfil de {username} atualizado e confirmado.")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Perfil de {username} já estava correto.")
                    )

        self.stdout.write(self.style.SUCCESS("Seeding de usuários do SGEA concluído."))

        # Cria tipos de evento
        tipos = [
            {"nome": "Palestra", "descricao": "Sessão expositiva com perguntas."},
            {"nome": "Minicurso", "descricao": "Aulas práticas de curta duração."},
            {"nome": "Workshop", "descricao": "Encontros com atividades práticas."},
            {"nome": "Semana Acadêmica", "descricao": "Série de eventos temáticos."},
        ]

        tipo_map = {}
        for t in tipos:
            obj, _ = TipoEvento.objects.get_or_create(nome=t["nome"], defaults={"descricao": t["descricao"]})
            tipo_map[t["nome"]] = obj

        # Cria eventos de exemplo
        try:
            organizador = User.objects.get(username="organizador@sgea.com")
            professor = User.objects.get(username="professor@sgea.com")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("Usuários base não encontrados; pulei criação de eventos."))
            return

        hoje = timezone.now().date()
        exemplos = [
            {
                "titulo": "Semana Acadêmica de Tecnologia",
                "descricao": "Trilha com mesas redondas, painéis de inovação e feira de projetos.",
                "tipo": "Semana Acadêmica",
                "inicio": hoje + timedelta(days=7),
                "fim": hoje + timedelta(days=11),
                "horario": "19:00",
                "local": "Auditório Central",
                "vagas": 120,
            },
            {
                "titulo": "Minicurso de Django REST",
                "descricao": "Construção de APIs com DRF, autenticação por token e throttling.",
                "tipo": "Minicurso",
                "inicio": hoje + timedelta(days=3),
                "fim": hoje + timedelta(days=4),
                "horario": "18:30",
                "local": "Lab 2 - Bloco B",
                "vagas": 35,
            },
            {
                "titulo": "Palestra: Segurança em Aplicações Web",
                "descricao": "Boas práticas de autenticação, OWASP Top 10 e exemplos em Python.",
                "tipo": "Palestra",
                "inicio": hoje + timedelta(days=14),
                "fim": hoje + timedelta(days=14),
                "horario": "20:00",
                "local": "Auditório 1",
                "vagas": 80,
            },
        ]

        for ev in exemplos:
            tipo_obj = tipo_map.get(ev["tipo"])
            evento, created = Evento.objects.get_or_create(
                titulo=ev["titulo"],
                defaults={
                    "TIPO": tipo_obj,
                    "descricao": ev["descricao"],
                    "data_inicio": ev["inicio"],
                    "data_fim": ev["fim"],
                    "horario": ev["horario"],
                    "local": ev["local"],
                    "vagas": ev["vagas"],
                    "organizador": organizador,
                    "responsavel": professor,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Evento criado: {evento.titulo}"))
            else:
                self.stdout.write(self.style.WARNING(f"Evento já existia: {evento.titulo}"))

        self.stdout.write(self.style.SUCCESS("Tipos e eventos de exemplo prontos."))
