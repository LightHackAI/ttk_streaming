from django.urls import path
from . import views

app_name = 'player'

urlpatterns = [
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('api/users/', views.get_users, name='get_users'),
    path('api/users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('api/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('api/users/<int:user_id>/change-password/', views.change_password, name='change_password'),
    path('api/users/<int:user_id>/assign-role/', views.assign_role, name='assign_role'),
    path('player/', views.player_page, name='player_page'),

    # Модуль ведущего
    path('host/', views.host_dashboard, name='host_dashboard'),

    # Медиатека
    path('api/media-files/', views.get_media_files, name='get_media_files'),
    path('api/media-files/upload/', views.upload_media, name='upload_media'),
    path('api/media-files/<int:file_id>/delete/', views.delete_media, name='delete_media'),

    # Плейлисты
    path('api/playlists/', views.get_playlists, name='get_playlists'),
    path('api/playlists/create/', views.create_playlist, name='create_playlist'),
    path('api/playlists/<int:playlist_id>/', views.get_playlist_items, name='get_playlist_items'),
    path('api/playlists/<int:playlist_id>/rename/', views.rename_playlist, name='rename_playlist'),
    path('api/playlists/<int:playlist_id>/delete/', views.delete_playlist, name='delete_playlist'),
    path('api/playlists/<int:playlist_id>/add/', views.add_to_playlist, name='add_to_playlist'),
    path('api/playlists/<int:playlist_id>/remove/<int:item_id>/', views.remove_from_playlist,
         name='remove_from_playlist'),
    path('api/playlists/<int:playlist_id>/reorder/', views.reorder_playlist, name='reorder_playlist'),
    path('api/playlists/<int:playlist_id>/toggle-setting/', views.toggle_playlist_setting,
         name='toggle_playlist_setting'),

    # Трансляция
    path('api/broadcast/start/', views.start_broadcast, name='start_broadcast'),
    path('api/broadcast/stop/', views.stop_broadcast, name='stop_broadcast'),
    path('api/broadcast/status/', views.get_broadcast_status, name='get_broadcast_status'),
    path('api/broadcast/volume/', views.set_volume, name='set_volume'),
    path('api/broadcast/video-start/', views.start_video_broadcast, name='start_video_broadcast'),

    # Аудиозаписи
    path('api/recordings/upload/', views.upload_audio_recording, name='upload_audio_recording'),
    path('api/recordings/', views.get_audio_recordings, name='get_audio_recordings'),

    # Сообщения
    path('api/messages/', views.get_messages, name='get_messages'),
    path('api/messages/<int:message_id>/status/', views.update_message_status, name='update_message_status'),
    path('api/broadcast/video-start/', views.start_video_broadcast, name='start_video_broadcast'),

    path('api/playlists/<int:playlist_id>/add-recording/', views.add_recording_to_playlist,
         name='add_recording_to_playlist'),
    path('api/recordings/<int:recording_id>/delete/', views.delete_recording, name='delete_recording'),
]