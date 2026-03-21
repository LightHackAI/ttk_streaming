from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from .forms import LoginForm, RegistrationForm
from .models import User


def login(request):
    """Страница авторизации"""
    if request.user.is_authenticated:
        return redirect('player:player_page')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Проверяем корректность данных в БД
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Добро пожаловать, {user.full_name}!')
                return redirect('player:player_page')
            else:
                messages.error(request, 'Неверный логин или пароль')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def register(request):
    """Страница регистрации"""
    if request.user.is_authenticated:
        return redirect('player:player_page')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти.')
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'Ошибка при регистрации: {str(e)}')
        else:
            # Выводим все ошибки формы
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_logout(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('accounts:login')