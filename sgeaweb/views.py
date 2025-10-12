# Views do SGEA — Sistema de Gestão de Eventos Acadêmicos

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.loader import get_template

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from .models import Evento, Inscricao, Certificado, PerfilUsuario, TipoEvento
from .forms import (UserRegisterForm, PerfilUsuarioForm, EventoForm)


def home(request):
    eventos = Evento.objects.all().order_by("data_inicio")
    return render(request, "sgeaweb/home.html", {"eventos": eventos})


def login_view(request):
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
    return render(request, "sgeaweb/usuario/login.html", {"next": next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu do sistema.")
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

            messages.success(request, "Cadastro realizado com sucesso. Faça login para continuar.")
            return redirect("login")
        else:
            messages.error(request, "Verifique os campos informados.")
    else:
        uform = UserRegisterForm()
        pform = PerfilUsuarioForm()
    return render(request, "sgeaweb/usuario/cadastro.html", {"uform": uform, "pform": pform})


def is_organizador(user: User) -> bool:
    try:
        return user.perfil.perfil == "ORGANIZADOR"
    except PerfilUsuario.DoesNotExist:
        return False


@user_passes_test(is_organizador)
def evento_list(request):
    eventos = Evento.objects.filter(organizador=request.user).order_by("-data_inicio")
    return render(request, "sgeaweb/evento/listar.html", {"eventos": eventos})


@user_passes_test(is_organizador)
def evento_create(request):
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
    ev = get_object_or_404(Evento, pk=pk, organizador=request.user)
    if request.method == "POST":
        ev.delete()
        messages.success(request, "Evento excluído com sucesso.")
        return redirect("evento_list")
    return render(request, "sgeaweb/evento/deletar.html", {"evento": ev})


@login_required
def evento_inscricoes(request, pk):
    ev = get_object_or_404(Evento, pk=pk, organizador=request.user)
    inscritos = Inscricao.objects.filter(evento=ev).select_related("participante")
    return render(request, "sgeaweb/evento/inscritos.html", {"evento": ev, "inscritos": inscritos})


@login_required
def inscrever(request, pk_evento):
    evento = get_object_or_404(Evento, pk=pk_evento)
    if request.method == "POST":
        Inscricao.objects.get_or_create(participante=request.user, evento=evento)
        messages.success(request, "Inscrição realizada com sucesso.")
        return redirect("minhas_inscricoes")
    return render(request, "sgeaweb/inscricao/inscrever.html", {"evento": evento})


@login_required
def minhas_inscricoes(request):
    insc = Inscricao.objects.filter(participante=request.user).select_related("evento")
    certs = {c.inscricao_id: c for c in Certificado.objects.filter(inscricao__in=insc)}
    for i in insc:
        i.certificado = certs.get(i.id)
    return render(request, "sgeaweb/inscricao/minhas.html", {"inscricoes": insc})


@user_passes_test(is_organizador)
def emitir_certificado(request, pk_inscricao):
    insc = get_object_or_404(Inscricao, pk=pk_inscricao, evento__organizador=request.user)
    cert, _ = Certificado.objects.get_or_create(
        inscricao=insc,
        defaults={'codigo_validacao': get_random_string(16)}
    )
    messages.success(request, f"Certificado emitido. Código: {cert.codigo_validacao}")
    return render(request, "sgeaweb/certificado/emitir.html", {"certificado": cert})


@login_required
def certificado_detalhe(request, pk_inscricao):
    insc = get_object_or_404(Inscricao, pk=pk_inscricao, participante=request.user)
    cert = get_object_or_404(Certificado, inscricao=insc)
    return render(
        request,
        "sgeaweb/certificado/detalhe.html",
        {"inscricao": insc, "certificado": cert}
    )


@login_required
def certificado_pdf(request, pk_inscricao):
    """Gera o PDF do certificado com ReportLab (sem dependências nativas)."""
    insc = get_object_or_404(Inscricao, pk=pk_inscricao, participante=request.user)
    cert = get_object_or_404(Certificado, inscricao=insc)

    aluno = request.user.get_full_name() or request.user.username
    evento = insc.evento

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    # Cabeçalho
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(w/2, h - 3*cm, "CERTIFICADO DE PARTICIPAÇÃO")

    p.setFont("Helvetica", 12)
    texto = (
        f"Certificamos que {aluno} participou do evento '{evento.titulo}', "
        f"realizado em {evento.data_inicio.strftime('%d/%m/%Y')}"
    )
    if evento.data_fim != evento.data_inicio:
        texto += f" a {evento.data_fim.strftime('%d/%m/%Y')}"
    texto += f", no local {evento.local}."
    p.drawString(2.5*cm, h - 5*cm, texto)

    # Código e rodapé
    p.setFont("Helvetica", 11)
    p.drawString(2.5*cm, h - 7*cm, f"Código de validação: {cert.codigo_validacao}")
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(2.5*cm, 2.2*cm, f"Emitido em {cert.emitido_em.strftime('%d/%m/%Y %H:%M')} — SGEA")

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="certificado_{cert.codigo_validacao}.pdf"'
    return resp
