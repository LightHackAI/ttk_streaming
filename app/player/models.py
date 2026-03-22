# player/models.py
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
import os


def user_media_path(instance, filename):
    return f'user_media/{instance.user.id}/{filename}'


class MediaFile(models.Model):
    MEDIA_TYPES = [
        ('audio', 'Аудио'),
        ('video', 'Видео'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='media_files')
    title = models.CharField(max_length=255, verbose_name='Название')
    file = models.FileField(upload_to=user_media_path, verbose_name='Файл')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, verbose_name='Тип медиа')
    duration = models.PositiveIntegerField(default=0, verbose_name='Длительность (сек)')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    is_deleted = models.BooleanField(default=False, verbose_name='Удален')

    class Meta:
        verbose_name = 'Медиафайл'
        verbose_name_plural = 'Медиафайлы'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    def delete(self, using=None, keep_parents=False):
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(using, keep_parents)


class Playlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='playlists')
    name = models.CharField(max_length=100, verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_active = models.BooleanField(default=False, verbose_name='Активен')
    loop = models.BooleanField(default=False, verbose_name='Зацикливание')
    shuffle = models.BooleanField(default=False, verbose_name='Перемешивание')
    is_playing = models.BooleanField(default=False, verbose_name='Воспроизводится')

    class Meta:
        verbose_name = 'Плейлист'
        verbose_name_plural = 'Плейлисты'

    def __str__(self):
        return self.name


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='items')
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name='playlist_items')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Элемент плейлиста'
        verbose_name_plural = 'Элементы плейлиста'
        ordering = ['order']

    def __str__(self):
        return f"{self.playlist.name} - {self.media_file.title}"


class Broadcast(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='broadcasts')
    playlist = models.ForeignKey(Playlist, on_delete=models.SET_NULL, null=True, blank=True, related_name='broadcasts')
    is_active = models.BooleanField(default=False, verbose_name='Активна')
    volume = models.PositiveIntegerField(default=70, validators=[MaxValueValidator(100), MinValueValidator(0)],
                                         verbose_name='Громкость')
    mic_enabled = models.BooleanField(default=False, verbose_name='Микрофон включен')
    cam_enabled = models.BooleanField(default=False, verbose_name='Камера включена')
    has_video = models.BooleanField(default=False, verbose_name='Есть видео')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Начало трансляции')
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name='Окончание трансляции')

    class Meta:
        verbose_name = 'Трансляция'
        verbose_name_plural = 'Трансляции'

    def __str__(self):
        return f"Трансляция {self.user.username} - {self.started_at}"


class AudioRecording(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='audio_recordings')
    title = models.CharField(max_length=255, verbose_name='Название')
    audio_file = models.FileField(upload_to='recordings/', verbose_name='Аудиозапись')
    duration = models.PositiveIntegerField(default=0, verbose_name='Длительность (сек)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата записи')
    added_to_playlist = models.BooleanField(default=False, verbose_name='Добавлен в плейлист')

    class Meta:
        verbose_name = 'Аудиозапись'
        verbose_name_plural = 'Аудиозаписи'

    def __str__(self):
        return self.title


class Message(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершено'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(verbose_name='Сообщение')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"