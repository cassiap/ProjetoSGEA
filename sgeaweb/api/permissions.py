from rest_framework.permissions import BasePermission


class IsOrganizador(BasePermission):
    """
    Permite acesso apenas a usuários com perfil ORGANIZADOR.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        try:
            return user.perfil.perfil == "ORGANIZADOR"
        except Exception:
            return False


class IsAlunoOuProfessor(BasePermission):
    """
    Permite que alunos e professores acessem operações permitidas.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        try:
            return user.perfil.perfil in ["ALUNO", "PROFESSOR"]
        except Exception:
            return False


class IsOwnerOrReadOnly(BasePermission):
    """
    Permite edição somente pelo organizador dono do evento.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # Se for evento, verifica organizador
        if hasattr(obj, "organizador"):
            return obj.organizador == request.user

        return False
