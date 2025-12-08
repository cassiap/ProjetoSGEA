# sgeaweb/forms.py

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.files.images import get_image_dimensions
from django.utils import timezone
import re

from .models import PerfilUsuario, Evento, Inscricao


# ======================
# FORMULÁRIO DE CADASTRO
# ======================
class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Digite uma senha"}),
        label="Senha"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirme a senha"}),
        label="Confirmar senha"
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

    # Validação do e-mail
    def clean_email(self):
        email = self.cleaned_data.get("email")
        validate_email(email)

        if User.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está cadastrado.")

        return email

    # Validação da senha
    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("password2")

        # Senhas iguais
        if p1 != p2:
            self.add_error("password2", "As senhas não coincidem.")

        # Regras de senha forte
        if p1:
            if len(p1) < 8:
                self.add_error("password", "A senha deve ter no mínimo 8 caracteres.")

            if not re.search(r"[A-Za-z]", p1):
                self.add_error("password", "A senha deve conter pelo menos uma letra.")

            if not re.search(r"\d", p1):
                self.add_error("password", "A senha deve conter pelo menos um número.")

            if not re.search(r"[^\w\s]", p1):
                self.add_error("password", "A senha deve conter pelo menos um caractere especial.")

        return cleaned


# ==============================
# FORMULÁRIO DE PERFIL DO USUÁRIO
# ==============================
class PerfilUsuarioForm(forms.ModelForm):
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
        telefone = self.cleaned_data.get("telefone", "")
        pattern = r"^\(\d{2}\)\s?\d{5}-\d{4}$"

        if not re.match(pattern, telefone):
            raise ValidationError("Informe o telefone no formato (XX) XXXXX-XXXX.")

        return telefone


# ======================
# FORMULÁRIO DE EVENTO
# ======================
class EventoForm(forms.ModelForm):
    banner = forms.ImageField(required=False, label="Banner do evento")

    class Meta:
        model = Evento
        fields = [
            "TIPO",
            "titulo",
            "descricao",
            "data_inicio",
            "data_fim",
            "horario",
            "local",
            "vagas",
            "responsavel",
            "banner",
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
            "responsavel": "Professor responsável",
            "banner": "Banner",
        }
        widgets = {
            "descricao": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Resumo do conteúdo do evento..."}
            ),
            "data_inicio": forms.DateInput(
                attrs={"type": "text", "class": "datepicker", "autocomplete": "off"}
            ),
            "data_fim": forms.DateInput(
                attrs={"type": "text", "class": "datepicker", "autocomplete": "off"}
            ),
            "horario": forms.TimeInput(
                attrs={"type": "text", "class": "timepicker", "autocomplete": "off"}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        data_inicio = cleaned.get("data_inicio")
        data_fim = cleaned.get("data_fim")
        hoje = timezone.now().date()

        if data_inicio and data_inicio < hoje:
            self.add_error("data_inicio", "A data de início não pode ser anterior ao dia atual.")

        if data_inicio and data_fim and data_fim < data_inicio:
            self.add_error("data_fim", "A data de término não pode ser anterior à data de início.")

        return cleaned

    def clean_vagas(self):
        vagas = self.cleaned_data.get("vagas")

        if vagas is not None and vagas <= 0:
            raise ValidationError("A quantidade de vagas deve ser maior que zero.")

        return vagas

    def clean_banner(self):
        banner = self.cleaned_data.get("banner")

        if banner:
            # Verifica se é realmente uma imagem
            if hasattr(banner, "content_type"):
                if not banner.content_type.startswith("image/"):
                    raise ValidationError("O arquivo enviado não é uma imagem válida.")

            # Tamanho máximo
            if banner.size > 3 * 1024 * 1024:
                raise ValidationError("A imagem deve ter até 3 MB.")

            # Dimensões mínimas
            w, h = get_image_dimensions(banner)
            if w < 400 or h < 300:
                raise ValidationError("A imagem é muito pequena (mínimo 400×300).")

        return banner


# ======================
# FORMULÁRIO DE INSCRIÇÃO
# ======================
class InscricaoForm(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = []
