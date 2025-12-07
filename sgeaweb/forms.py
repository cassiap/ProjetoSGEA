from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.files.images import get_image_dimensions
from .models import PerfilUsuario, Evento, Inscricao
import re


class UserRegisterForm(forms.ModelForm):
    """Formulário de criação de usuário."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Digite uma senha"}),
        label="Senha"
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]
        labels = {
            "username": "Usuário",
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "email": "E-mail",
        }
        help_texts = {"username": ""}

    def clean_email(self):
        """Valida formato e unicidade do e-mail."""
        email = self.cleaned_data.get("email")
        validate_email(email)
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está cadastrado.")
        return email


class PerfilUsuarioForm(forms.ModelForm):
    """Dados complementares do usuário."""
    class Meta:
        model = PerfilUsuario
        fields = ["telefone", "instituicao", "perfil"]
        labels = {
            "telefone": "Telefone",
            "instituicao": "Instituição",
            "perfil": "Perfil",
        }
        widgets = {
            "telefone": forms.TextInput(
                attrs={
                    "placeholder": "(61) 99999-9999",
                    "class": "telefone-mask",
                    "maxlength": "15",
                }
            ),
        }

    def clean_telefone(self):
        """Valida o formato (XX) XXXXX-XXXX."""
        telefone = self.cleaned_data.get("telefone", "")
        pattern = r"^\(\d{2}\)\s?\d{5}-\d{4}$"
        if not re.match(pattern, telefone):
            raise ValidationError("Informe o telefone no formato (XX) XXXXX-XXXX.")
        return telefone


class EventoForm(forms.ModelForm):
    """Formulário de criação/edição de evento."""
    banner = forms.ImageField(required=False, label="Banner do evento")

    class Meta:
        model = Evento
        fields = [
            "TIPO", "titulo", "descricao", "data_inicio", "data_fim",
            "horario", "local", "vagas", "banner"
        ]
        labels = {
            "TIPO": "Tipo do evento",
            "titulo": "Título",
            "descricao": "Descrição",
            "data_inicio": "Data de início",
            "data_fim": "Data de término",
            "horario": "Horário",
            "local": "Local",
            "vagas": "Quantidade de vagas",
            "banner": "Banner",
        }
        widgets = {
            "descricao": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Resumo do conteúdo do evento..."
                }
            ),
            "data_inicio": forms.DateInput(
                attrs={
                    "type": "text",
                    "class": "datepicker",
                    "autocomplete": "off",
                    "placeholder": "AAAA-MM-DD",
                }
            ),
            "data_fim": forms.DateInput(
                attrs={
                    "type": "text",
                    "class": "datepicker",
                    "autocomplete": "off",
                    "placeholder": "AAAA-MM-DD",
                }
            ),
            "horario": forms.TimeInput(
                attrs={
                    "type": "text",
                    "class": "timepicker",
                    "autocomplete": "off",
                    "placeholder": "HH:MM",
                }
            ),
        }

    def clean_vagas(self):
        vagas = self.cleaned_data.get("vagas")
        if vagas is not None and vagas <= 0:
            raise ValidationError("A quantidade de vagas deve ser maior que zero.")
        return vagas

    def clean_banner(self):
        """Verifica se o arquivo é imagem e tem tamanho razoável."""
        banner = self.cleaned_data.get("banner")
        if banner:
            if not banner.content_type.startswith("image/"):
                raise ValidationError("O arquivo enviado não é uma imagem válida.")
            if banner.size > 3 * 1024 * 1024:
                raise ValidationError("A imagem deve ter até 3 MB.")
            w, h = get_image_dimensions(banner)
            if w < 400 or h < 300:
                raise ValidationError("A imagem é muito pequena (mínimo 400×300).")
        return banner


class InscricaoForm(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = []
