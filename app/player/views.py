from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
import json
from accounts.models import User


@login_required
def admin_panel(request):
    if not request.user.is_admin():
        return redirect('player:player_page')
    return render(request, 'player/admin_panel.html')


@login_required
@require_http_methods(["GET"])
def get_users(request):
    if not request.user.is_admin():
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)

    users = User.objects.filter(is_deleted=False).order_by('-date_joined')

    # Фильтрация
    login = request.GET.get('login', '')
    if login:
        users = users.filter(username__icontains=login)

    fullname = request.GET.get('fullname', '')
    if fullname:
        users = users.filter(full_name__icontains=fullname)

    role = request.GET.get('role', '')
    if role:
        users = users.filter(role=role)

    reg_date = request.GET.get('reg_date', '')
    if reg_date:
        users = users.filter(date_joined__date=reg_date)

    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'login': user.username,
            'fullname': user.full_name,
            'role': user.role,
            'regDate': user.date_joined.strftime('%Y-%m-%d'),
        })

    return JsonResponse({'users': users_data})


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def edit_user(request, user_id):
    if not request.user.is_admin():
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)

    try:
        data = json.loads(request.body)
        user = get_object_or_404(User, id=user_id, is_deleted=False)

        login = data.get('login', '').strip()
        if login:
            if not login.isalnum():
                return JsonResponse({'error': 'Логин должен содержать только латинские буквы и цифры'}, status=400)
            if User.objects.filter(username=login).exclude(id=user_id).exists():
                return JsonResponse({'error': 'Пользователь с таким логином уже существует'}, status=400)
            user.username = login

        fullname = data.get('fullname', '').strip()
        if fullname:
            if not all(c.isalpha() or c.isspace() for c in fullname):
                return JsonResponse({'error': 'ФИО должно содержать только русские буквы'}, status=400)
            user.full_name = fullname

        user.save()

        return JsonResponse({
            'success': True,
            'message': 'Пользователь успешно обновлен',
            'user': {
                'id': user.id,
                'login': user.username,
                'fullname': user.full_name,
                'role': user.role,
                'regDate': user.date_joined.strftime('%Y-%m-%d'),
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["DELETE"])
@csrf_exempt
def delete_user(request, user_id):
    if not request.user.is_admin():
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)

    try:
        user = get_object_or_404(User, id=user_id)

        if user.id == request.user.id:
            return JsonResponse({'error': 'Нельзя удалить самого себя'}, status=400)

        user.is_deleted = True
        user.deleted_at = timezone.now()  # Исправлено: добавлен импорт timezone
        user.save()

        return JsonResponse({
            'success': True,
            'message': 'Пользователь успешно удален'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def change_password(request, user_id):
    if not request.user.is_admin():
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)

    try:
        data = json.loads(request.body)
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')

        user = get_object_or_404(User, id=user_id, is_deleted=False)

        if not user.check_password(old_password):
            return JsonResponse({'error': 'Неверный старый пароль'}, status=400)

        if len(new_password) < 6:
            return JsonResponse({'error': 'Пароль должен содержать минимум 6 символов'}, status=400)

        if new_password != confirm_password:
            return JsonResponse({'error': 'Пароли не совпадают'}, status=400)

        user.set_password(new_password)
        user.save()

        if user.id == request.user.id:
            update_session_auth_hash(request, user)

        return JsonResponse({
            'success': True,
            'message': 'Пароль успешно изменен'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def assign_role(request, user_id):
    if not request.user.is_admin():
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)

    try:
        data = json.loads(request.body)
        new_role = data.get('role', '')

        if new_role not in ['user', 'leader', 'admin']:
            return JsonResponse({'error': 'Недопустимая роль'}, status=400)

        user = get_object_or_404(User, id=user_id, is_deleted=False)
        user.role = new_role
        user.save()

        return JsonResponse({
            'success': True,
            'message': 'Роль успешно назначена',
            'role': user.role
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def player_page(request):
    return render(request, 'player/player_page.html')