from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.crypto import get_random_string

from sgeaweb.models import Evento, Inscricao, Certificado, Auditoria


class Command(BaseCommand):
    help = "Emite certificados automaticamente para eventos já encerrados (presença confirmada)."

    def handle(self, *args, **options):
        hoje = timezone.now().date()
        eventos = Evento.objects.filter(data_fim__lte=hoje)
        total_emitidos = 0

        for ev in eventos:
            inscritos = Inscricao.objects.filter(evento=ev, presenca_confirmada=True)
            for insc in inscritos:
                cert, created = Certificado.objects.get_or_create(
                    inscricao=insc,
                    defaults={"codigo_validacao": get_random_string(16)}
                )
                if created:
                    total_emitidos += 1
                    try:
                        Auditoria.objects.create(
                            usuario=ev.organizador,
                            acao="CERTIFICADO_GERADO_AUTO_CMD",
                            descricao=f"Evento #{ev.id} - Inscrição #{insc.id} - Código {cert.codigo_validacao}"
                        )
                    except Exception:
                        pass

        self.stdout.write(self.style.SUCCESS(f"Certificados emitidos: {total_emitidos}"))
