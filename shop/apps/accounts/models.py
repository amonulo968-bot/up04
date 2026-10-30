from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомный пользователь магазина: сотрудник с ролью."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Администратор"
        MANAGER = "manager", "Менеджер"
        DIRECTOR = "director", "Директор"

    phone = models.CharField("Телефон", max_length=20, blank=True)
    role = models.CharField(
        "Роль", max_length=20,
        choices=Role.choices, default=Role.MANAGER,
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
