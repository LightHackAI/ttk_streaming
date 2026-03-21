from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


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
                regex=r'^[А-Яа-я\s]+$',
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

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username