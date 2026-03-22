import re

from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
import json
import os
from accounts.models import User
from .models import MediaFile, Playlist, PlaylistItem, Broadcast, AudioRecording, Message
import subprocess
import json as json_lib


def is_leader_or_admin(user):
    return user.is_authenticated and (user.role == 'leader' or user.role == 'admin')


def get_audio_duration(file_path):
    try:
        # Пробуем через mutagen
        import mutagen
        try:
            if file_path.lower().endswith('.mp3'):
                audio = mutagen.mp3.MP3(file_path)
                return int(audio.info.length)
            elif file_path.lower().endswith('.wav'):
                audio = mutagen.wave.WAVE(file_path)
                return int(audio.info.length)
            elif file_path.lower().endswith('.ogg'):
                audio = mutagen.oggvorbis.OggVorbis(file_path)
                return int(audio.info.length)
        except:
            pass

    except Exception as e:
        print(f"Error getting duration: {e}")

    return 0


def get_video_duration(file_path):
    try:
        import cv2
        cap = cv2.VideoCapture(file_path)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            if fps > 0 and frame_count > 0:
                return int(frame_count / fps)
    except:
        pass

    # Пробуем через ffprobe
    try:
        import subprocess
        import json
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', file_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    duration = float(stream.get('duration', 0))
                    if duration > 0:
                        return int(duration)
    except:
        pass

    return 0


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
            if not re.match(r'^[А-Яа-яЁё\s]+$', fullname):
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
        user.deleted_at = timezone.now()
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


@login_required
@user_passes_test(is_leader_or_admin)
def host_dashboard(request):
    return render(request, 'player/host_dashboard.html')


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["GET"])
def get_media_files(request):
    media_type = request.GET.get('type', '')
    user_id = request.GET.get('user_id', request.user.id)

    files = MediaFile.objects.filter(user_id=user_id, is_deleted=False)
    if media_type:
        files = files.filter(media_type=media_type)

    files_data = [{
        'id': f.id,
        'title': f.title,
        'file_url': f.file.url,
        'media_type': f.media_type,
        'duration': f.duration,
        'uploaded_at': f.uploaded_at.strftime('%Y-%m-%d %H:%M'),
    } for f in files]

    return JsonResponse({'files': files_data})


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["POST"])
@csrf_exempt
def upload_media(request):
    try:
        file = request.FILES.get('file')
        title = request.POST.get('title', '')
        media_type = request.POST.get('media_type', 'audio')
        duration = request.POST.get('duration', 0)

        if not file:
            return JsonResponse({'error': 'Файл не выбран'}, status=400)

        max_size = 50 * 1024 * 1024 if media_type == 'audio' else 1000 * 1024 * 1024
        if file.size > max_size:
            return JsonResponse({'error': f'Размер файла превышает {max_size // (1024 * 1024)} МБ'}, status=400)

        valid_extensions = {
            'audio': ['mp3', 'wav', 'ogg', 'webm'],
            'video': ['mp4', 'webm']
        }

        ext = file.name.split('.')[-1].lower()
        if ext not in valid_extensions.get(media_type, []):
            return JsonResponse({'error': 'Неподдерживаемый формат файла'}, status=400)

        if not title:
            title = file.name.rsplit('.', 1)[0]

        media_file = MediaFile.objects.create(
            user=request.user,
            title=title,
            file=file,
            media_type=media_type,
            duration=int(duration) if duration else 0
        )

        return JsonResponse({
            'success': True,
            'message': 'Файл успешно загружен',
            'file': {
                'id': media_file.id,
                'title': media_file.title,
                'file_url': media_file.file.url,
                'media_type': media_file.media_type,
                'duration': media_file.duration,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["DELETE"])
@csrf_exempt
def delete_media(request, file_id):
    try:
        media_file = get_object_or_404(MediaFile, id=file_id, user=request.user)

        # Физическое удаление файла
        if media_file.file and os.path.isfile(media_file.file.path):
            try:
                os.remove(media_file.file.path)
            except Exception as e:
                print(f"Ошибка удаления файла: {e}")

        # Мягкое удаление из БД
        media_file.is_deleted = True
        media_file.save()

        return JsonResponse({'success': True, 'message': 'Файл удален'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["GET"])
def get_playlists(request):
    playlists = Playlist.objects.filter(user=request.user)

    playlists_data = [{
        'id': p.id,
        'name': p.name,
        'is_active': p.is_active,
        'loop': p.loop,
        'shuffle': p.shuffle,
        'is_playing': p.is_playing,
        'items_count': p.items.count(),
        'created_at': p.created_at.strftime('%Y-%m-%d %H:%M'),
    } for p in playlists]

    return JsonResponse({'playlists': playlists_data})


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["POST"])
@csrf_exempt
def create_playlist(request):
    try:
        data = json.loads(request.body)
        name = data.get('name', '')

        if not name:
            return JsonResponse({'error': 'Название плейлиста обязательно'}, status=400)

        playlist = Playlist.objects.create(user=request.user, name=name)

        return JsonResponse({
            'success': True,
            'message': 'Плейлист создан',
            'playlist': {
                'id': playlist.id,
                'name': playlist.name,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["GET"])
def get_playlist_items(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    items = playlist.items.select_related('media_file').all()

    items_data = [{
        'id': item.id,
        'order': item.order,
        'media_file': {
            'id': item.media_file.id,
            'title': item.media_file.title,
            'file_url': item.media_file.file.url,
            'media_type': item.media_file.media_type,
            'duration': item.media_file.duration,
        }
    } for item in items]

    return JsonResponse({
        'playlist': {
            'id': playlist.id,
            'name': playlist.name,
            'loop': playlist.loop,
            'shuffle': playlist.shuffle,
            'is_playing': playlist.is_playing,
        },
        'items': items_data
    })


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["POST"])
@csrf_exempt
def add_to_playlist(request, playlist_id):
    try:
        data = json.loads(request.body)
        media_ids = data.get('media_ids', [])

        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)

        # Получаем текущий максимальный порядок
        existing_items = playlist.items.all()
        current_max_order = existing_items.aggregate(models.Max('order'))['order__max']
        if current_max_order is None:
            current_max_order = 0

        for idx, media_id in enumerate(media_ids):
            # Проверяем, существует ли файл в медиатеке
            media_file = get_object_or_404(MediaFile, id=media_id, user=request.user, is_deleted=False)

            # Проверяем, не добавлен ли уже этот файл
            if not playlist.items.filter(media_file=media_file).exists():
                PlaylistItem.objects.create(
                    playlist=playlist,
                    media_file=media_file,
                    order=current_max_order + idx + 1
                )

        return JsonResponse({'success': True, 'message': 'Файлы добавлены в плейлист'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["DELETE"])
@csrf_exempt
def remove_from_playlist(request, playlist_id, item_id):
    try:
        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
        item = get_object_or_404(PlaylistItem, id=item_id, playlist=playlist)
        item.delete()

        return JsonResponse({'success': True, 'message': 'Файл удален из плейлиста'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["POST"])
@csrf_exempt
def reorder_playlist(request, playlist_id):
    try:
        data = json.loads(request.body)
        items_order = data.get('items_order', [])

        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)

        for order_data in items_order:
            PlaylistItem.objects.filter(id=order_data['id'], playlist=playlist).update(order=order_data['order'])

        return JsonResponse({'success': True, 'message': 'Порядок обновлен'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["POST"])
@csrf_exempt
def toggle_playlist_setting(request, playlist_id):
    try:
        data = json.loads(request.body)
        setting = data.get('setting')
        value = data.get('value')

        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)

        if setting in ['loop', 'shuffle']:
            setattr(playlist, setting, value)
            playlist.save()

        return JsonResponse({'success': True, 'message': f'{setting} обновлен'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["POST"])
@csrf_exempt
def start_broadcast(request):
    try:
        data = json.loads(request.body)
        playlist_id = data.get('playlist_id')

        playlist = None
        if playlist_id:
            playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)

        Broadcast.objects.filter(user=request.user, is_active=True).update(is_active=False, ended_at=timezone.now())

        broadcast = Broadcast.objects.create(
            user=request.user,
            playlist=playlist,
            is_active=True,
            volume=data.get('volume', 70)
        )

        if playlist:
            playlist.is_playing = True
            playlist.is_active = True
            playlist.save()

        return JsonResponse({
            'success': True,
            'message': 'Трансляция запущена',
            'broadcast_id': broadcast.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["POST"])
@csrf_exempt
def stop_broadcast(request):
    try:
        broadcast = get_object_or_404(Broadcast, user=request.user, is_active=True)
        broadcast.is_active = False
        broadcast.ended_at = timezone.now()
        broadcast.save()

        if broadcast.playlist:
            broadcast.playlist.is_playing = False
            broadcast.playlist.is_active = False
            broadcast.playlist.save()

        return JsonResponse({'success': True, 'message': 'Трансляция остановлена'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["GET"])
def get_broadcast_status(request):
    broadcast = Broadcast.objects.filter(user=request.user, is_active=True).first()

    if broadcast:
        return JsonResponse({
            'is_active': True,
            'broadcast_id': broadcast.id,
            'playlist_id': broadcast.playlist.id if broadcast.playlist else None,
            'volume': broadcast.volume,
            'started_at': broadcast.started_at.strftime('%Y-%m-%d %H:%M')
        })

    return JsonResponse({'is_active': False})


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["POST"])
@csrf_exempt
def set_volume(request):
    try:
        data = json.loads(request.body)
        volume = data.get('volume', 70)

        if not 0 <= volume <= 100:
            return JsonResponse({'error': 'Громкость должна быть от 0 до 100'}, status=400)

        broadcast = Broadcast.objects.filter(user=request.user, is_active=True).first()
        if broadcast:
            broadcast.volume = volume
            broadcast.save()

        return JsonResponse({'success': True, 'volume': volume})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["POST"])
@csrf_exempt
def upload_audio_recording(request):
    try:
        file = request.FILES.get('audio')
        title = request.POST.get('title', '')

        if not file:
            return JsonResponse({'error': 'Аудиофайл не найден'}, status=400)

        if not title:
            title = f"Запись {timezone.now().strftime('%Y-%m-%d %H:%M')}"

        recording = AudioRecording.objects.create(
            user=request.user,
            title=title,
            audio_file=file
        )

        # Попытка получить длительность через ffprobe
        try:
            import subprocess
            import json as json_lib
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', recording.audio_file.path],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                data = json_lib.loads(result.stdout)
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'audio':
                        duration = float(stream.get('duration', 0))
                        recording.duration = int(duration)
                        recording.save()
                        break
        except:
            pass

        return JsonResponse({
            'success': True,
            'message': 'Запись сохранена',
            'recording': {
                'id': recording.id,
                'title': recording.title,
                'file_url': recording.audio_file.url,
                'duration': recording.duration,
                'created_at': recording.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["GET"])
def get_audio_recordings(request):
    recordings = AudioRecording.objects.filter(user=request.user)

    recordings_data = [{
        'id': r.id,
        'title': r.title,
        'file_url': r.audio_file.url,
        'duration': r.duration,
        'created_at': r.created_at.strftime('%Y-%m-%d %H:%M'),
        'added_to_playlist': r.added_to_playlist
    } for r in recordings]

    return JsonResponse({'recordings': recordings_data})


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["GET"])
def get_messages(request):
    status = request.GET.get('status', '')
    archived = request.GET.get('archived', 'false') == 'true'

    messages = Message.objects.all()

    if archived:
        messages = messages.filter(status='completed')
    else:
        messages = messages.exclude(status='completed')

    if status:
        messages = messages.filter(status=status)

    messages_data = [{
        'id': m.id,
        'user_id': m.user.id,
        'username': m.user.username,
        'content': m.content,
        'status': m.status,
        'created_at': m.created_at.strftime('%Y-%m-%d %H:%M'),
        'updated_at': m.updated_at.strftime('%Y-%m-%d %H:%M'),
    } for m in messages]

    return JsonResponse({'messages': messages_data})


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["POST"])
@csrf_exempt
def update_message_status(request, message_id):
    try:
        data = json.loads(request.body)
        new_status = data.get('status')

        if new_status not in ['new', 'in_progress', 'completed']:
            return JsonResponse({'error': 'Недопустимый статус'}, status=400)

        message = get_object_or_404(Message, id=message_id)
        message.status = new_status
        message.save()

        return JsonResponse({
            'success': True,
            'message': 'Статус обновлен',
            'status': message.status
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# Добавить в конец файла player/views.py:

@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["PUT"])
@csrf_exempt
def rename_playlist(request, playlist_id):
    try:
        data = json.loads(request.body)
        new_name = data.get('name', '').strip()

        if not new_name:
            return JsonResponse({'error': 'Название не может быть пустым'}, status=400)

        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
        playlist.name = new_name
        playlist.save()

        return JsonResponse({
            'success': True,
            'message': 'Плейлист переименован',
            'name': playlist.name
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["DELETE"])
@csrf_exempt
def delete_playlist(request, playlist_id):
    try:
        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)

        if playlist.is_active:
            return JsonResponse({'error': 'Нельзя удалить активный плейлист'}, status=400)

        playlist.delete()

        return JsonResponse({
            'success': True,
            'message': 'Плейлист удален'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["POST"])
@csrf_exempt
def start_video_broadcast(request):
    try:
        data = json.loads(request.body)

        # Здесь будет логика запуска видеотрансляции
        # Пока просто сохраняем статус

        return JsonResponse({
            'success': True,
            'message': 'Видеотрансляция запущена'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["POST"])
@csrf_exempt
def start_video_broadcast(request):
    try:
        data = json.loads(request.body)

        # TODO: Здесь будет интеграция с плеером для запуска видеотрансляции
        # Пока просто заглушка
        print(f"Запуск видеотрансляции с параметрами: {data}")

        return JsonResponse({
            'success': True,
            'message': 'Видеотрансляция запущена (заглушка)'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["POST"])
@csrf_exempt
def add_recording_to_playlist(request, playlist_id):
    try:
        data = json.loads(request.body)
        recording_id = data.get('recording_id')

        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
        recording = get_object_or_404(AudioRecording, id=recording_id, user=request.user)

        # Создаем медиафайл из записи
        media_file = MediaFile.objects.create(
            user=request.user,
            title=recording.title,
            file=recording.audio_file,
            media_type='audio',
            duration=recording.duration
        )

        # Получаем текущий максимальный порядок
        current_max_order = playlist.items.aggregate(models.Max('order'))['order__max'] or 0

        PlaylistItem.objects.create(
            playlist=playlist,
            media_file=media_file,
            order=current_max_order + 1
        )

        recording.added_to_playlist = True
        recording.save()

        return JsonResponse({'success': True, 'message': 'Запись добавлена в плейлист'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_leader_or_admin)
@require_http_methods(["DELETE"])
@csrf_exempt
def delete_recording(request, recording_id):
    try:
        recording = get_object_or_404(AudioRecording, id=recording_id, user=request.user)

        # Удаляем файл с диска
        if recording.audio_file and os.path.isfile(recording.audio_file.path):
            os.remove(recording.audio_file.path)

        recording.delete()

        return JsonResponse({'success': True, 'message': 'Запись удалена'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)