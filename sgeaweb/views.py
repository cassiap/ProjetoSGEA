from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.conf import settings

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from .models import Evento, Inscricao, Certificado, PerfilUsuario, Auditoria
from .forms import UserRegisterForm, PerfilUsuarioForm, EventoForm


#Auditoria
def log_action(user, acao: str, descricao: str):
    try:
        Auditoria.objects.create(usuario=user if user.is_authenticated else None,
                                 acao=acao,
                                 descricao=descricao)
    except Exception:
        # Evita quebrar fluxo em caso de erro de log
        pass


#Envio de e-mail de confirmação
def enviar_email_confirmacao(usuario, token):
    assunto = "Confirme seu cadastro no SGEA"
    remetente = "naoresponda@sgea.com"
    destinatario = [usuario.email]
    base_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")
    confirm_link = f"{base_url}/confirmar/{token}"
    logo_url = f"{base_url}{static('sgeaweb/img/logo-sgea.png')}"
    contexto = {
        "usuario": usuario,
        "token": token,
        "confirm_link": confirm_link,
        "logo_url": logo_url,
    }

    html = render_to_string("email/confirmacao.html", contexto)
    email = EmailMultiAlternatives(assunto, "", remetente, destinatario)
    email.attach_alternative(html, "text/html")
    email.send()


# Home
def home(request):
    eventos = Evento.objects.all().order_by("data_inicio")
    return render(request, "sgeaweb/home.html", {"eventos": eventos})


#Autenticação
def login_view(request):
    next_url = request.GET.get("next", request.POST.get("next", ""))

    if request.method == "POST":
        user = authenticate(
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            if not user.perfil.email_confirmado:
                messages.error(request, "Confirme seu e-mail antes de entrar.")
                return redirect("login")

            login(request, user)
            messages.success(request, "Login realizado com sucesso.")
            log_action(user, "LOGIN", "Usuário realizou login no sistema.")
            return redirect(next_url or "home")

        messages.error(request, "Credenciais inválidas.")

    return render(request, "sgeaweb/usuario/login.html", {"next": next_url})


def logout_view(request):
    log_action(request.user, "LOGOUT", "Usuário saiu do sistema.")
    logout(request)
    messages.info(request, "Você saiu do sistema.")
    return redirect("home")


#Cadastro + confirmação de e-mail
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
            perfil.confirma_token = get_random_string(48)
            perfil.save()

            log_action(user, "CRIAR_USUARIO", f"Novo usuário criado: {user.username} ({perfil.perfil}).")

            enviar_email_confirmacao(user, perfil.confirma_token)
            messages.success(request, "Cadastro realizado! Verifique seu e-mail para confirmar sua conta.")
            return redirect("login")

        messages.error(request, "Verifique os campos informados.")
    else:
        uform = UserRegisterForm()
        pform = PerfilUsuarioForm()

    return render(request, "sgeaweb/usuario/cadastro.html", {"uform": uform, "pform": pform})


def confirmar_email(request, token):
    perfil = get_object_or_404(PerfilUsuario, confirma_token=token)
    perfil.email_confirmado = True
    perfil.confirma_token = None
    perfil.save()
    log_action(perfil.user, "CONFIRMAR_EMAIL", f"E-mail confirmado para {perfil.user.username}.")
    messages.success(request, "E-mail confirmado! Agora você pode acessar sua conta.")
    return redirect("login")


#Permissão Organizador
def is_organizador(user: User) -> bool:
    try:
        return user.perfil.perfil == "ORGANIZADOR" and user.perfil.email_confirmado
    except PerfilUsuario.DoesNotExist:
        return False


#Eventos
@user_passes_test(is_organizador)
def evento_list(request):
    eventos = Evento.objects.filter(organizador=request.user).order_by("-data_inicio")
    return render(request, "sgeaweb/evento/listar.html", {"eventos": eventos})


@user_passes_test(is_organizador)
def evento_create(request):
    if request.method == "POST":
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.organizador = request.user
            ev.responsavel = form.cleaned_data["responsavel"]
            ev.save()
            log_action(request.user, "CADASTRAR_EVENTO", f"Evento criado: {ev.titulo} (ID {ev.id}).")
            messages.success(request, "Evento criado com sucesso.")
            return redirect("evento_list")
        messages.error(request, "Não foi possível salvar o evento.")
    else:
        form = EventoForm()

    return render(request, "sgeaweb/evento/criar.html", {"form": form})


@user_passes_test(is_organizador)
def evento_update(request, pk):
    ev = get_object_or_404(Evento, pk=pk)
    if ev.organizador != request.user:
        return HttpResponseForbidden("Você não pode editar este evento.")

    if request.method == "POST":
        form = EventoForm(request.POST, request.FILES, instance=ev)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.responsavel = form.cleaned_data["responsavel"]
            ev.save()
            log_action(request.user, "ALTERAR_EVENTO", f"Evento alterado: {ev.titulo} (ID {ev.id}).")
            messages.success(request, "Evento atualizado.")
            return redirect("evento_list")
        messages.error(request, "Erro ao atualizar evento.")
    else:
        form = EventoForm(instance=ev)

    return render(request, "sgeaweb/evento/editar.html", {"form": form})


@user_passes_test(is_organizador)
def evento_delete(request, pk):
    ev = get_object_or_404(Evento, pk=pk)
    if ev.organizador != request.user:
        return HttpResponseForbidden("Você não pode excluir este evento.")

    if request.method == "POST":
        titulo = ev.titulo
        _id = ev.id
        ev.delete()
        log_action(request.user, "EXCLUIR_EVENTO", f"Evento excluído: {titulo} (ID {_id}).")
        messages.success(request, "Evento excluído.")
        return redirect("evento_list")

    return render(request, "sgeaweb/evento/deletar.html", {"evento": ev})


def evento_detalhe(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    return render(request, "sgeaweb/evento/detalhe.html", {"evento": evento})


#  Inscrições
@login_required
def evento_inscricoes(request, pk):
    ev = get_object_or_404(Evento, pk=pk)

    if ev.organizador != request.user:
        return HttpResponseForbidden("Não autorizado.")

    inscritos = (Inscricao.objects
                 .filter(evento=ev)
                 .select_related("participante", "certificado"))
    # trocado para 'inscricoes.html'
    return render(request, "sgeaweb/evento/inscricoes.html", {"evento": ev, "inscritos": inscritos})



@login_required
def inscrever(request, pk_evento):
    evento = get_object_or_404(Evento, pk=pk_evento)

    if evento.data_fim < timezone.now().date():
        messages.error(request, "Este evento já foi encerrado.")
        return redirect("home")

    if request.user == evento.organizador:
        messages.error(request, "Organizadores não podem se inscrever.")
        return redirect("home")

    if Inscricao.objects.filter(evento=evento, participante=request.user).exists():
        messages.info(request, "Você já está inscrito.")
        return redirect("minhas_inscricoes")

    if Inscricao.objects.filter(evento=evento).count() >= evento.vagas:
        messages.error(request, "Vagas esgotadas.")
        return redirect("home")

    if request.method == "POST":
        insc = Inscricao.objects.create(participante=request.user, evento=evento)
        log_action(request.user, "INSCRICAO_EVENTO", f"Inscrição no evento ID {evento.id} - {evento.titulo}.")
        messages.success(request, "Inscrição realizada.")
        return redirect("minhas_inscricoes")

    return render(request, "sgeaweb/inscricao/inscrever.html", {"evento": evento})


#Minhas inscrições 
@login_required
def minhas_inscricoes(request):
    insc = (Inscricao.objects
            .filter(participante=request.user)
            .select_related("evento"))

    # Emissão automática de certificados 
    hoje = timezone.now().date()
    for i in insc:
        if i.evento.data_fim <= hoje and i.presenca_confirmada:
            cert, created = Certificado.objects.get_or_create(
                inscricao=i,
                defaults={"codigo_validacao": get_random_string(16)}
            )
            if created:
                log_action(request.user, "GERAR_CERTIFICADO",
                          f"Certificado autoemitido para inscrição {i.id} (evento {i.evento.id}).")

        # anexa para facilitar o template
        i.certificado = getattr(i, "certificado", None) or Certificado.objects.filter(inscricao=i).first()

    return render(request, "sgeaweb/inscricao/minhas.html", {"inscricoes": insc})


#Certificados
@user_passes_test(is_organizador)
def emitir_certificado(request, pk_inscricao):
    insc = get_object_or_404(Inscricao, pk=pk_inscricao)
    if insc.evento.organizador != request.user:
        return HttpResponseForbidden("Não autorizado.")

    cert, created = Certificado.objects.get_or_create(
        inscricao=insc,
        defaults={"codigo_validacao": get_random_string(16)}
    )

    if created:
        messages.success(request, f"Certificado emitido! Código: {cert.codigo_validacao}")
        log_action(request.user, "GERAR_CERTIFICADO",
                  f"Certificado emitido manualmente para inscrição {insc.id}.")
    else:
        messages.info(request, "Este certificado já existia.")

    return render(request, "sgeaweb/certificado/emitir.html", {"certificado": cert})


@login_required
def certificado_detalhe(request, pk_inscricao):
    insc = get_object_or_404(Inscricao, pk=pk_inscricao)
    if insc.participante != request.user:
        return HttpResponseForbidden("Não autorizado.")

    cert = get_object_or_404(Certificado, inscricao=insc)
    log_action(request.user, "CONSULTAR_CERTIFICADO",
               f"Usuário consultou certificado (inscrição {insc.id}).")
    return render(request, "sgeaweb/certificado/detalhe.html", {"inscricao": insc, "certificado": cert})


@login_required
def certificado_pdf(request, pk_inscricao):
    insc = get_object_or_404(Inscricao, pk=pk_inscricao)
    if insc.participante != request.user:
        return HttpResponseForbidden("Não autorizado.")

    cert = get_object_or_404(Certificado, inscricao=insc)
    aluno = request.user.get_full_name() or request.user.username
    evento = insc.evento

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(w / 2, h - 3 * cm, "CERTIFICADO DE PARTICIPAÇÃO")

    p.setFont("Helvetica", 12)
    texto = (
        f"Certificamos que {aluno} participou do evento '{evento.titulo}', "
        f"realizado em {evento.data_inicio.strftime('%d/%m/%Y')}"
    )
    if evento.data_fim != evento.data_inicio:
        texto += f" a {evento.data_fim.strftime('%d/%m/%Y')}"
    texto += f", no local {evento.local}."
    p.drawString(2.5 * cm, h - 5 * cm, texto)

    p.setFont("Helvetica", 11)
    p.drawString(2.5 * cm, h - 7 * cm, f"Código de validação: {cert.codigo_validacao}")
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(2.5 * cm, 2.2 * cm, f"Emitido em {cert.emitido_em.strftime('%d/%m/%Y %H:%M')} — SGEA")

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="certificado_{cert.codigo_validacao}.pdf"'
    log_action(request.user, "BAIXAR_CERTIFICADO_PDF",
               f"Usuário baixou PDF do certificado (inscrição {insc.id}).")
    return resp


# Tela do Organizador
@user_passes_test(is_organizador)
def auditoria_list(request):
    qs = Auditoria.objects.all().select_related("usuario")
    # filtros simples por data e usuário
    dia = request.GET.get("dia")  # formato YYYY-MM-DD
    usuario = request.GET.get("usuario")  # username

    if dia:
        try:
            d = timezone.datetime.fromisoformat(dia).date()
            qs = qs.filter(data_hora__date=d)
        except Exception:
            messages.error(request, "Data inválida no filtro (use YYYY-MM-DD).")

    if usuario:
        qs = qs.filter(usuario__username__icontains=usuario)

    qs = qs.order_by("-data_hora")[:500]  # limite de segurança
    return render(request, "sgeaweb/auditoria/listar.html", {"registros": qs})
