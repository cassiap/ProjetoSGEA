# sgeaweb/api/views.py
from rest_framework import generics, permissions
from rest_framework.throttling import UserRateThrottle
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from django.utils import timezone

from sgeaweb.models import Evento, Inscricao
from sgeaweb.views import log_action
from .serializers import EventoListSerializer, InscricaoCreateSerializer
from .permissions import IsAlunoOuProfessor


class ObtainAuthTokenBrowsable(ObtainAuthToken):
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]


class EventoListThrottle(UserRateThrottle):
    scope = "eventos_list"


class InscricaoCreateThrottle(UserRateThrottle):
    scope = "inscricoes_create"


class EventoListAPI(generics.ListAPIView):
    queryset = Evento.objects.all().order_by("data_inicio")
    serializer_class = EventoListSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [EventoListThrottle]

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        log_action(request.user, "API_CONSULTA_EVENTOS",
                   f"Listagem via API em {timezone.now().isoformat()}.")
        return resp


class InscricaoCreateAPI(generics.CreateAPIView):
    queryset = Inscricao.objects.all()
    serializer_class = InscricaoCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAlunoOuProfessor]
    throttle_classes = [InscricaoCreateThrottle]

    def perform_create(self, serializer):
        obj = serializer.save()
        log_action(self.request.user, "API_INSCRICAO_EVENTO",
                   f"Inscrição via API no evento {obj.evento_id}.")
