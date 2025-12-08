from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from sgeaweb.models import TipoEvento, Evento

class Command(BaseCommand):
    help = "Cria tipos e eventos de demonstração (precisa rodar após seed_sgea)."

    def handle(self, *args, **opts):
        hoje = timezone.now().date()

        tipos = [
            ("Palestra", "Apresentações e talks curtos."),
            ("Minicurso", "Aulas práticas de curta duração."),
            ("Workshop", "Atividades mão na massa."),
        ]
        tipo_objs = {}
        for nome, desc in tipos:
            t, _ = TipoEvento.objects.get_or_create(nome=nome, defaults={"descricao": desc})
            tipo_objs[nome] = t
        self.stdout.write(self.style.SUCCESS("Tipos criados/garantidos."))

        # Usuários criados no seed_sgea.py
        org = User.objects.filter(username="organizador@sgea.com").first()
        prof = User.objects.filter(username="professor@sgea.com").first()

        if not org or not prof:
            self.stdout.write(self.style.ERROR(
                "Usuários demo não encontrados. Rode primeiro: python manage.py seed_sgea"
            ))
            return

        eventos_demo = [
            {
                "TIPO": tipo_objs["Palestra"],
                "titulo": "Boas práticas de Django 5",
                "descricao": "Cobertura de validação, DRF e deploy básico.",
                "data_inicio": hoje + timedelta(days=7),
                "data_fim": hoje + timedelta(days=7),
                "horario": "19:00",
                "local": "Auditório 1",
                "vagas": 50,
                "organizador": org,
                "responsavel": prof,
            },
            {
                "TIPO": tipo_objs["Minicurso"],
                "titulo": "APIs com DRF do zero",
                "descricao": "Serializers, autenticação por token, throttling e testes.",
                "data_inicio": hoje + timedelta(days=10),
                "data_fim": hoje + timedelta(days=11),
                "horario": "18:30",
                "local": "Lab 3",
                "vagas": 30,
                "organizador": org,
                "responsavel": prof,
            },
            {
                "TIPO": tipo_objs["Workshop"],
                "titulo": "Gerando PDFs com ReportLab",
                "descricao": "Prática de certificados com layout e validação.",
                "data_inicio": hoje + timedelta(days=14),
                "data_fim": hoje + timedelta(days=14),
                "horario": "20:00",
                "local": "Sala Multiuso",
                "vagas": 25,
                "organizador": org,
                "responsavel": prof,
            },
        ]

        criados = 0
        for data in eventos_demo:
            obj, created = Evento.objects.get_or_create(
                titulo=data["titulo"], defaults=data
            )
            if created:
                criados += 1

        self.stdout.write(self.style.SUCCESS(f"{criados} evento(s) criados."))
        self.stdout.write(self.style.SUCCESS("Pronto!"))
