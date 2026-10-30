from rest_framework.permissions import BasePermission


class IsDirectorOrAdmin(BasePermission):
    """Доступ к отчётам: только директор, администратор или суперпользователь."""

    message = "Доступ только для директора и администратора."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.is_superuser or user.role in ("admin", "director")
