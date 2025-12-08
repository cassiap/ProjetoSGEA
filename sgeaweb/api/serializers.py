# sgeaweb/api/serializers.py — COMPLETO
from rest_framework import serializers
from django.utils import timezone
from sgeaweb.models import Evento, Inscricao, TipoEvento


class TipoEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEvento
        fields = ["id", "nome", "descricao"]


class EventoSerializer(serializers.ModelSerializer):
    tipo_id = serializers.PrimaryKeyRelatedField(
        source="TIPO",
        queryset=TipoEvento.objects.all(),
        write_only=True
    )
    tipo_nome = serializers.CharField(source="TIPO.nome", read_only=True)
    organizador = serializers.CharField(source="organizador.username", read_only=True)
    responsavel_nome = serializers.SerializerMethodField(read_only=True)
    banner_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Evento
        fields = [
            "id",
            "tipo_id",
            "tipo_nome",
            "titulo",
            "descricao",
            "data_inicio",
            "data_fim",
            "horario",
            "local",
            "vagas",
            "organizador",
            "responsavel_nome",
            "banner_url",
        ]

    def get_responsavel_nome(self, obj):
        if obj.responsavel:
            return obj.responsavel.get_full_name() or obj.responsavel.username
        return None

    def get_banner_url(self, obj):
        request = self.context.get("request")
        if getattr(obj, "banner", None) and getattr(obj.banner, "url", None):
            # retorna URL absoluta para funcionar fora do site também
            if request:
                return request.build_absolute_uri(obj.banner.url)
            return obj.banner.url
        return None


class InscricaoSerializer(serializers.ModelSerializer):
    participante = serializers.CharField(source="participante.username", read_only=True)
    evento_titulo = serializers.CharField(source="evento.titulo", read_only=True)

    class Meta:
        model = Inscricao
        fields = [
            "id",
            "participante",
            "evento",
            "evento_titulo",
            "criado_em",
        ]
        extra_kwargs = {
            "evento": {"write_only": True},
        }


class EventoListSerializer(EventoSerializer):
    class Meta(EventoSerializer.Meta):
        pass


class InscricaoCreateSerializer(serializers.Serializer):
    """
    POST /api/inscricoes/
    {
        "evento_id": 1
    }
    """
    evento_id = serializers.IntegerField()

    def validate_evento_id(self, value):
        try:
            Evento.objects.get(pk=value)
        except Evento.DoesNotExist:
            raise serializers.ValidationError("Evento não encontrado.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        usuario = request.user
        evento = Evento.objects.get(pk=validated_data["evento_id"])

        # Regras de negócio (mesmas do HTML)
        if evento.data_fim < timezone.now().date():
            raise serializers.ValidationError("Este evento já foi encerrado.")

        if usuario == evento.organizador:
            raise serializers.ValidationError("Organizadores não podem se inscrever no próprio evento.")

        if Inscricao.objects.filter(evento=evento, participante=usuario).exists():
            raise serializers.ValidationError("Você já está inscrito neste evento.")

        if Inscricao.objects.filter(evento=evento).count() >= evento.vagas:
            raise serializers.ValidationError("Não há vagas disponíveis.")

        return Inscricao.objects.create(participante=usuario, evento=evento)
