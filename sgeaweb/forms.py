# Formulários do SGEA (cadastro de usuário, perfil e eventos)

from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario, Evento, Inscricao


class UserRegisterForm(forms.ModelForm):
    """
    Formulário de criação de usuário do Django.
    A senha é tratada como PasswordInput para não aparecer em texto puro.
    """
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
        help_texts = {
            "username": "",  # remove o help_text padrão do Django
        }


class PerfilUsuarioForm(forms.ModelForm):
    """
    Dados complementares do usuário (telefone, instituição e perfil).
    """
    class Meta:
        model = PerfilUsuario
        fields = ["telefone", "instituicao", "perfil"]
        labels = {
            "telefone": "Telefone",
            "instituicao": "Instituição",
            "perfil": "Perfil",
        }


class EventoForm(forms.ModelForm):
    """
    Formulário para criar/editar eventos.
    Atribuí widgets para melhorar a experiência (date pickers e textarea).
    """
    class Meta:
        model = Evento
        fields = ["TIPO", "titulo", "descricao", "data_inicio", "data_fim", "horario", "local", "vagas"]
        labels = {
            "TIPO": "Tipo do evento",
            "titulo": "Título",
            "descricao": "Descrição",
            "data_inicio": "Data de início",
            "data_fim": "Data de término",
            "horario": "Horário",
            "local": "Local",
            "vagas": "Quantidade de vagas",
        }
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 4, "placeholder": "Resumo do conteúdo do evento..."}),
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
            "data_fim": forms.DateInput(attrs={"type": "date"}),
        }


class InscricaoForm(forms.ModelForm):
    """
    Não expomos campos, pois o participante e o evento são definidos na view.
    """
    class Meta:
        model = Inscricao
        fields = []
