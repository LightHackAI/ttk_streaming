from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('leader', 'Ведущий'),
        ('admin', 'Администратор'),
    ]

    full_name = models.CharField(
        max_length=255,
        verbose_name='ФИО',
        validators=[
            RegexValidator(
                regex=r'^[А-Яа-яЁё\s]+$',
                message='ФИО должно содержать только русские буквы'
            )
        ]
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Роль'
    )
    # Поле для мягкого удаления
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Удален'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата удаления'
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата регистрации'
    )

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def is_admin(self):
        """Проверка, является ли пользователь администратором"""
        return self.role == 'admin'