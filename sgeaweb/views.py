# Views do SGEA — Sistema de Gestão de Eventos Acadêmicos

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User

from .models import Evento, Inscricao, Certificado, PerfilUsuario, TipoEvento
from .forms import (UserRegisterForm, PerfilUsuarioForm, EventoForm)


def home(request):
    """Página inicial listando eventos disponíveis."""
    eventos = Evento.objects.all().order_by("data_inicio")
    return render(request, "sgeaweb/home.html", {"eventos": eventos})


def login_view(request):
    """Tela de login simples usando o auth do Django."""
    # Se a pessoa foi redirecionada de uma página protegida, o Django envia ?next=/rota
    next_url = request.GET.get("next", request.POST.get("next", ""))

    if request.method == "POST":
        user = authenticate(
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            messages.success(request, "Login realizado com sucesso.")
            return redirect(next_url or "home")
        messages.error(request, "Credenciais inválidas.")
    # OBS.: se quiser, dá pra incluir <input type="hidden" name="next" value="{{ request.GET.next }}">
    # no template login.html. Mantive simples como no exemplo.
    return render(request, "sgeaweb/usuario/login.html", {"next": next_url})


def logout_view(request):
    """Encerra a sessão do usuário."""
    logout(request)
    messages.info(request, "Você saiu do sistema.")
    return redirect("home")


def cadastro_view(request):
    """Cadastro do usuário + criação do perfil complementar."""
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

            messages.success(request, "Cadastro realizado com sucesso. Faça login para continuar.")
            return redirect("login")
        else:
            messages.error(request, "Verifique os campos informados.")
    else:
        uform = UserRegisterForm()
        pform = PerfilUsuarioForm()
    return render(request, "sgeaweb/usuario/cadastro.html", {"uform": uform, "pform": pform})


def is_organizador(user: User) -> bool:
    """Checagem de permissão: apenas organizadores acessam o CRUD de eventos."""
    try:
        return user.perfil.perfil == "ORGANIZADOR"
    except PerfilUsuario.DoesNotExist:
        # Se o usuário não tem perfil ainda, não é organizador.
        return False


@user_passes_test(is_organizador)
def evento_list(request):
    """Lista de eventos criados pelo organizador logado."""
    eventos = Evento.objects.filter(organizador=request.user).order_by("-data_inicio")
    return render(request, "sgeaweb/evento/listar.html", {"eventos": eventos})


@user_passes_test(is_organizador)
def evento_create(request):
    """Criação de um novo evento."""
    if request.method == "POST":
        form = EventoForm(request.POST)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.organizador = request.user
            ev.save()
            messages.success(request, "Evento criado com sucesso.")
            return redirect("evento_list")
        messages.error(request, "Não foi possível salvar. Verifique os campos.")
    else:
        form = EventoForm()
    return render(request, "sgeaweb/evento/criar.html", {"form": form})


@user_passes_test(is_organizador)
def evento_update(request, pk):
    """Edição de um evento do organizador."""
    ev = get_object_or_404(Evento, pk=pk, organizador=request.user)
    if request.method == "POST":
        form = EventoForm(request.POST, instance=ev)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento atualizado com sucesso.")
            return redirect("evento_list")
        messages.error(request, "Não foi possível atualizar. Confira os dados.")
    else:
        form = EventoForm(instance=ev)
    return render(request, "sgeaweb/evento/editar.html", {"form": form})


@user_passes_test(is_organizador)
def evento_delete(request, pk):
    """Confirmação e exclusão de um evento do organizador."""
    ev = get_object_or_404(Evento, pk=pk, organizador=request.user)
    if request.method == "POST":
        ev.delete()
        messages.success(request, "Evento excluído com sucesso.")
        return redirect("evento_list")
    return render(request, "sgeaweb/evento/deletar.html", {"evento": ev})


@login_required
def inscrever(request, pk_evento):
    """Inscrição do usuário logado em um evento específico."""
    evento = get_object_or_404(Evento, pk=pk_evento)

    # (Opcional) Regra simples de lotação:
    # if Inscricao.objects.filter(evento=evento).count() >= evento.vagas:
    #     messages.error(request, "Não há vagas disponíveis para este evento.")
    #     return redirect("home")

    if request.method == "POST":
        Inscricao.objects.get_or_create(participante=request.user, evento=evento)
        messages.success(request, "Inscrição realizada com sucesso.")
        return redirect("minhas_inscricoes")
    return render(request, "sgeaweb/inscricao/inscrever.html", {"evento": evento})


@login_required
def minhas_inscricoes(request):
    """Lista as inscrições do usuário logado."""
    insc = Inscricao.objects.filter(participante=request.user).select_related("evento")
    return render(request, "sgeaweb/inscricao/minhas.html", {"inscricoes": insc})


@user_passes_test(is_organizador)
def emitir_certificado(request, pk_inscricao):
    """Emissão de certificado (apenas organizador do evento pode emitir)."""
    insc = get_object_or_404(Inscricao, pk=pk_inscricao, evento__organizador=request.user)
    cert, _ = Certificado.objects.get_or_create(
        inscricao=insc,
        defaults={'codigo_validacao': get_random_string(16)}
    )
    messages.success(request, f"Certificado emitido. Código: {cert.codigo_validacao}")
    return render(request, "sgeaweb/certificado/emitir.html", {"certificado": cert})
