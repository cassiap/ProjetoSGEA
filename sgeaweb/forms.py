from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario, Evento, Inscricao

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ["telefone", "instituicao", "perfil"]

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ["TIPO", "titulo", "descricao", "data_inicio", "data_fim", "horario", "local", "vagas"]

class InscricaoForm(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = []
