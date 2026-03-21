from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите ваш логин',
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль',
            'autocomplete': 'new-password'
        })
    )


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Придумайте пароль',
            'autocomplete': 'new-password'
        }),
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};:""\\|,.<>\/?]+$',
                message='Пароль может содержать только латинские буквы, цифры и символы'
            )
        ]
    )
    confirm_password = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Повторите пароль',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'full_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].validators.append(
            RegexValidator(
                regex=r'^[A-Za-z]+$',
                message='Логин должен содержать только латинские буквы'
            )
        )
        self.fields['full_name'].validators.append(
            RegexValidator(
                regex=r'^[А-Яа-я\s]+$',
                message='ФИО должно содержать только русские буквы'
            )
        )
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Придумайте логин',
        })
        self.fields['full_name'].widget.attrs.update({
            'placeholder': 'Иванов Иван Иванович',
        })

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError('Пароли не совпадают')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Хеширование пароля
        user.role = 'user'  # Устанавливаем роль "Пользователь" по умолчанию
        if commit:
            user.save()
        return user