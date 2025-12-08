# sgeaweb/management/commands/seed_sgea.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from sgeaweb.models import PerfilUsuario


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

            # ============================
            #   CRIAÇÃO OU ATUALIZAÇÃO DO USER
            # ============================
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

            # ============================
            #   CRIA OU ATUALIZA PERFIL
            # ============================
            perfil, perfil_created = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={
                    "telefone": "(61) 99999-9999",
                    "instituicao": instituicao,
                    "perfil": perfil_tipo,
                    "email_confirmado": True,   # ✔️ marca como confirmado
                    "confirma_token": None,     # ✔️ sem token necessário
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
