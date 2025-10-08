from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User

from .models import Evento, Inscricao, Certificado, PerfilUsuario, TipoEvento
from .forms import (UserRegisterForm, PerfilUsuarioForm, EventoForm)

def home(request):
    eventos = Evento.objects.all()
    return render(request, "sgeaweb/home.html", {"eventos": eventos})

def login_view(request):
    if request.method == "POST":
        user = authenticate(username=request.POST.get("username"),
                            password=request.POST.get("password"))
        if user:
            login(request, user)
            return redirect("home")
        messages.error(request, "Credenciais inválidas.")
    return render(request, "sgeaweb/usuario/login.html")

def logout_view(request):
    logout(request)
    return redirect("home")

def cadastro_view(request):
    if request.method == "POST":
        uform = UserRegisterForm(request.POST)
        pform = PerfilUsuarioForm(request.POST)
        if uform.is_valid() and pform.is_valid():
            user = uform.save(commit=False)
            user.set_password(uform.cleaned_data["password"])
            user.save()
            perfil = pform.save(commit=False)
            perfil.user = user
            perfil.save()
            messages.success(request, "Cadastro realizado. Faça login.")
            return redirect("login")
    else:
        uform = UserRegisterForm()
        pform = PerfilUsuarioForm()
    return render(request, "sgeaweb/usuario/cadastro.html", {"uform": uform, "pform": pform})

def is_organizador(user):
    try:
        return user.perfil.perfil == "ORGANIZADOR"
    except PerfilUsuario.DoesNotExist:
        return False

@user_passes_test(is_organizador)
def evento_list(request):
    eventos = Evento.objects.filter(organizador=request.user)
    return render(request, "sgeaweb/evento/listar.html", {"eventos": eventos})

@user_passes_test(is_organizador)
def evento_create(request):
    if request.method == "POST":
        form = EventoForm(request.POST)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.organizador = request.user
            ev.save()
            messages.success(request, "Evento criado.")
            return redirect("evento_list")
    else:
        form = EventoForm()
    return render(request, "sgeaweb/evento/criar.html", {"form": form})

@user_passes_test(is_organizador)
def evento_update(request, pk):
    ev = get_object_or_404(Evento, pk=pk, organizador=request.user)
    if request.method == "POST":
        form = EventoForm(request.POST, instance=ev)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento atualizado.")
            return redirect("evento_list")
    else:
        form = EventoForm(instance=ev)
    return render(request, "sgeaweb/evento/editar.html", {"form": form})

@user_passes_test(is_organizador)
def evento_delete(request, pk):
    ev = get_object_or_404(Evento, pk=pk, organizador=request.user)
    if request.method == "POST":
        ev.delete()
        messages.success(request, "Evento excluído.")
        return redirect("evento_list")
    return render(request, "sgeaweb/evento/deletar.html", {"evento": ev})

@login_required
def inscrever(request, pk_evento):
    evento = get_object_or_404(Evento, pk=pk_evento)
    if request.method == "POST":
        Inscricao.objects.get_or_create(participante=request.user, evento=evento)
        messages.success(request, "Inscrição realizada.")
        return redirect("minhas_inscricoes")
    return render(request, "sgeaweb/inscricao/inscrever.html", {"evento": evento})

@login_required
def minhas_inscricoes(request):
    insc = Inscricao.objects.filter(participante=request.user).select_related("evento")
    return render(request, "sgeaweb/inscricao/minhas.html", {"inscricoes": insc})

@user_passes_test(is_organizador)
def emitir_certificado(request, pk_inscricao):
    insc = get_object_or_404(Inscricao, pk=pk_inscricao, evento__organizador=request.user)
    cert, _ = Certificado.objects.get_or_create(
        inscricao=insc,
        defaults={'codigo_validacao': get_random_string(16)}
    )
    messages.success(request, f"Certificado emitido: {cert.codigo_validacao}")
    return render(request, "sgeaweb/certificado/emitir.html", {"certificado": cert})
