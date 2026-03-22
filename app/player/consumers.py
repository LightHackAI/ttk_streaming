# player/consumers.py
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from .models import Broadcast, Playlist, PlaylistItem, MediaFile
from accounts.models import User
import logging

logger = logging.getLogger(__name__)


class BroadcastConsumer(AsyncWebsocketConsumer):
    """Consumer для управления трансляцией ведущего"""

    async def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        if not (self.user.role == 'leader' or self.user.role == 'admin'):
            await self.close()
            return

        self.room_group_name = f'user_{self.user.id}_broadcast'

        # Присоединяемся к комнате
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"BroadcastConsumer connected for user {self.user.id}")

    async def disconnect(self, close_code):
        # Покидаем комнату
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Если был активный эфир, останавливаем его
        await self.stop_broadcast()

        logger.info(f"BroadcastConsumer disconnected for user {self.user.id}")

    async def receive(self, text_data):
        """Получение сообщений от ведущего"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'start_broadcast':
                await self.start_broadcast(data)
            elif action == 'stop_broadcast':
                await self.stop_broadcast()
            elif action == 'toggle_mic':
                await self.toggle_mic(data.get('enabled', False))
            elif action == 'toggle_cam':
                await self.toggle_cam(data.get('enabled', False))
            elif action == 'set_volume':
                await self.set_volume(data.get('volume', 70))
            elif action == 'playlist_item_changed':
                await self.playlist_item_changed(data)
            elif action == 'webrtc_offer':
                await self.handle_webrtc_offer(data)
            elif action == 'webrtc_answer':
                await self.handle_webrtc_answer(data)
            elif action == 'webrtc_ice_candidate':
                await self.handle_ice_candidate(data)

        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error in receive: {e}")

    async def start_broadcast(self, data):
        """Начать трансляцию"""
        playlist_id = data.get('playlist_id')
        volume = data.get('volume', 70)

        # Останавливаем предыдущие трансляции
        await self.stop_broadcast()

        # Создаем новую трансляцию
        broadcast = await self.create_broadcast(playlist_id, volume)

        if broadcast:
            self.broadcast_id = broadcast['id']
            self.playlist_id = playlist_id

            # Отправляем подтверждение ведущему
            await self.send(json.dumps({
                'type': 'broadcast_started',
                'broadcast_id': self.broadcast_id,
                'playlist_id': playlist_id
            }))

            # Уведомляем слушателей о начале трансляции
            await self.channel_layer.group_send(
                'stream_listeners',
                {
                    'type': 'broadcast_status',
                    'action': 'started',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'user_avatar': self.user.username[0].upper(),
                    'broadcast_type': 'video' if data.get('cam_enabled') else 'audio',
                    'playlist_id': playlist_id
                }
            )

            # Если есть плейлист, начинаем его воспроизведение
            if playlist_id:
                await self.start_playlist(playlist_id)

    async def stop_broadcast(self):
        """Остановить трансляцию"""
        if hasattr(self, 'broadcast_id'):
            await self.end_broadcast(self.broadcast_id)

            # Уведомляем слушателей об остановке
            await self.channel_layer.group_send(
                'stream_listeners',
                {
                    'type': 'broadcast_status',
                    'action': 'stopped',
                    'user_id': self.user.id
                }
            )

            delattr(self, 'broadcast_id')

        if hasattr(self, 'playlist_playing'):
            delattr(self, 'playlist_playing')

    async def toggle_mic(self, enabled):
        """Включить/выключить микрофон"""
        await self.update_mic_status(enabled)

        await self.channel_layer.group_send(
            f'user_{self.user.id}_stream',
            {
                'type': 'mic_status',
                'enabled': enabled,
                'user_id': self.user.id
            }
        )

    async def toggle_cam(self, enabled):
        """Включить/выключить камеру"""
        await self.update_cam_status(enabled)

        await self.channel_layer.group_send(
            f'user_{self.user.id}_stream',
            {
                'type': 'cam_status',
                'enabled': enabled,
                'user_id': self.user.id
            }
        )

    async def set_volume(self, volume):
        """Установить громкость"""
        await self.update_broadcast_volume(self.broadcast_id, volume)

    async def playlist_item_changed(self, data):
        """Изменение элемента плейлиста"""
        item_id = data.get('item_id')
        media_file = await self.get_media_file(item_id)

        if media_file:
            await self.channel_layer.group_send(
                'stream_listeners',
                {
                    'type': 'playlist_item',
                    'user_id': self.user.id,
                    'media_file': media_file
                }
            )

    async def handle_webrtc_offer(self, data):
        """Обработка WebRTC offer от ведущего"""
        offer = data.get('offer')
        listener_id = data.get('listener_id')

        # Отправляем offer конкретному слушателю
        await self.channel_layer.send(
            f'listener_{listener_id}',
            {
                'type': 'webrtc_offer',
                'offer': offer,
                'user_id': self.user.id
            }
        )

    async def handle_webrtc_answer(self, data):
        """Обработка WebRTC answer от слушателя"""
        answer = data.get('answer')
        listener_id = data.get('listener_id')

        # Отправляем answer ведущему
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_answer',
                'answer': answer,
                'listener_id': listener_id
            }
        )

    async def handle_ice_candidate(self, data):
        """Обработка ICE candidate"""
        candidate = data.get('candidate')
        listener_id = data.get('listener_id')

        # Отправляем ICE candidate ведущему
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'ice_candidate',
                'candidate': candidate,
                'listener_id': listener_id
            }
        )

    async def start_playlist(self, playlist_id):
        """Начать воспроизведение плейлиста"""
        self.playlist_playing = True
        items = await self.get_playlist_items(playlist_id)

        for item in items:
            if not self.playlist_playing:
                break

            # Отправляем информацию о текущем треке слушателям
            await self.channel_layer.group_send(
                'stream_listeners',
                {
                    'type': 'playlist_item',
                    'user_id': self.user.id,
                    'media_file': item
                }
            )

            # Ждем длительность трека
            await asyncio.sleep(item['duration'])

    @sync_to_async
    def create_broadcast(self, playlist_id, volume):
        """Создать трансляцию в БД"""
        from .models import Broadcast, Playlist

        playlist = None
        if playlist_id:
            try:
                playlist = Playlist.objects.get(id=playlist_id, user=self.user)
            except Playlist.DoesNotExist:
                pass

        broadcast = Broadcast.objects.create(
            user=self.user,
            playlist=playlist,
            is_active=True,
            volume=volume,
            mic_enabled=False,
            cam_enabled=False
        )

        return {
            'id': broadcast.id,
            'playlist_id': playlist_id,
            'volume': volume
        }

    @sync_to_async
    def end_broadcast(self, broadcast_id):
        """Завершить трансляцию"""
        from .models import Broadcast
        from django.utils import timezone

        try:
            broadcast = Broadcast.objects.get(id=broadcast_id, user=self.user)
            broadcast.is_active = False
            broadcast.ended_at = timezone.now()
            broadcast.save()

            if broadcast.playlist:
                broadcast.playlist.is_playing = False
                broadcast.playlist.is_active = False
                broadcast.playlist.save()
        except Broadcast.DoesNotExist:
            pass

    @sync_to_async
    def update_broadcast_volume(self, broadcast_id, volume):
        """Обновить громкость трансляции"""
        from .models import Broadcast

        try:
            broadcast = Broadcast.objects.get(id=broadcast_id, user=self.user)
            broadcast.volume = volume
            broadcast.save()
        except Broadcast.DoesNotExist:
            pass

    @sync_to_async
    def update_mic_status(self, enabled):
        """Обновить статус микрофона"""
        from .models import Broadcast

        try:
            broadcast = Broadcast.objects.get(user=self.user, is_active=True)
            broadcast.mic_enabled = enabled
            broadcast.save()
        except Broadcast.DoesNotExist:
            pass

    @sync_to_async
    def update_cam_status(self, enabled):
        """Обновить статус камеры"""
        from .models import Broadcast

        try:
            broadcast = Broadcast.objects.get(user=self.user, is_active=True)
            broadcast.cam_enabled = enabled
            broadcast.save()
        except Broadcast.DoesNotExist:
            pass

    @sync_to_async
    def get_playlist_items(self, playlist_id):
        """Получить элементы плейлиста"""
        from .models import Playlist

        items = []
        try:
            playlist = Playlist.objects.get(id=playlist_id, user=self.user)
            for item in playlist.items.select_related('media_file').all():
                items.append({
                    'id': item.media_file.id,
                    'title': item.media_file.title,
                    'file_url': item.media_file.file.url,
                    'media_type': item.media_file.media_type,
                    'duration': item.media_file.duration
                })
        except Playlist.DoesNotExist:
            pass

        return items

    @sync_to_async
    def get_media_file(self, item_id):
        """Получить медиафайл по ID элемента плейлиста"""
        from .models import PlaylistItem

        try:
            item = PlaylistItem.objects.select_related('media_file').get(id=item_id)
            return {
                'id': item.media_file.id,
                'title': item.media_file.title,
                'file_url': item.media_file.file.url,
                'media_type': item.media_file.media_type,
                'duration': item.media_file.duration
            }
        except PlaylistItem.DoesNotExist:
            return None

    async def new_message(self, event):
        """Получение нового сообщения от слушателя"""
        await self.send(json.dumps({
            'type': 'new_message',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'username': event['username'],
            'content': event['content'],
            'created_at': event['created_at']
        }))

    # Обработчики для сообщений от группы
    async def listener_joined(self, event):
        """Уведомление о присоединении слушателя"""
        await self.send(json.dumps({
            'type': 'listener_joined',
            'listener_id': event['listener_id'],
            'listener_name': event['listener_name']
        }))

    async def listener_left(self, event):
        """Уведомление о выходе слушателя"""
        await self.send(json.dumps({
            'type': 'listener_left',
            'listener_id': event['listener_id']
        }))

    async def webrtc_answer(self, event):
        """Получение WebRTC answer от слушателя"""
        await self.send(json.dumps({
            'type': 'webrtc_answer',
            'listener_id': event['listener_id'],
            'answer': event['answer']
        }))

    async def ice_candidate(self, event):
        """Получение ICE candidate от слушателя"""
        await self.send(json.dumps({
            'type': 'ice_candidate',
            'listener_id': event['listener_id'],
            'candidate': event['candidate']
        }))


class StreamConsumer(AsyncWebsocketConsumer):
    """Consumer для прослушивания трансляций"""

    async def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_group_name = 'stream_listeners'
        self.listener_group = f'listener_{self.user.id}'

        # Присоединяемся к комнате слушателей
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Присоединяемся к личной комнате для WebRTC
        await self.channel_layer.group_add(
            self.listener_group,
            self.channel_name
        )

        await self.accept()

        # Отправляем список активных трансляций
        await self.send_active_broadcasts()

        logger.info(f"StreamConsumer connected for user {self.user.id}")

    async def disconnect(self, close_code):
        # Покидаем комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.listener_group,
            self.channel_name
        )

        logger.info(f"StreamConsumer disconnected for user {self.user.id}")

    async def receive(self, text_data):
        """Получение сообщений от слушателя"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'join_stream':
                await self.join_stream(data.get('user_id'))
            elif action == 'leave_stream':
                await self.leave_stream()
            elif action == 'send_message':
                await self.send_message(data.get('message'))
            elif action == 'webrtc_answer':
                await self.handle_webrtc_answer(data)
            elif action == 'ice_candidate':
                await self.handle_ice_candidate(data)

        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error in receive: {e}")

    async def join_stream(self, broadcaster_id):
        """Присоединиться к трансляции ведущего"""
        self.current_broadcaster = broadcaster_id

        # Уведомляем ведущего о новом слушателе
        await self.channel_layer.group_send(
            f'user_{broadcaster_id}_broadcast',
            {
                'type': 'listener_joined',
                'listener_id': self.user.id,
                'listener_name': self.user.username
            }
        )

        # Получаем информацию о трансляции
        broadcast_info = await self.get_broadcast_info(broadcaster_id)

        if broadcast_info:
            await self.send(json.dumps({
                'type': 'stream_info',
                'broadcaster': broadcast_info
            }))

    async def leave_stream(self):
        """Покинуть трансляцию"""
        if hasattr(self, 'current_broadcaster'):
            await self.channel_layer.group_send(
                f'user_{self.current_broadcaster}_broadcast',
                {
                    'type': 'listener_left',
                    'listener_id': self.user.id
                }
            )
            delattr(self, 'current_broadcaster')

    async def send_message(self, message):
        """Отправить сообщение ведущему"""
        if hasattr(self, 'current_broadcaster'):
            # Сохраняем сообщение в БД
            saved_message = await self.save_message(message)

            # Отправляем сообщение ведущему
            await self.channel_layer.group_send(
                f'user_{self.current_broadcaster}_broadcast',
                {
                    'type': 'new_message',
                    'message_id': saved_message['id'],
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'content': message,
                    'created_at': saved_message['created_at']
                }
            )

            await self.send(json.dumps({
                'type': 'message_sent',
                'success': True
            }))

    async def handle_webrtc_answer(self, data):
        """Обработка WebRTC answer для ведущего"""
        answer = data.get('answer')
        broadcaster_id = data.get('broadcaster_id')

        await self.channel_layer.group_send(
            f'user_{broadcaster_id}_broadcast',
            {
                'type': 'webrtc_answer',
                'answer': answer,
                'listener_id': self.user.id
            }
        )

    async def handle_ice_candidate(self, data):
        """Обработка ICE candidate для ведущего"""
        candidate = data.get('candidate')
        broadcaster_id = data.get('broadcaster_id')

        await self.channel_layer.group_send(
            f'user_{broadcaster_id}_broadcast',
            {
                'type': 'ice_candidate',
                'candidate': candidate,
                'listener_id': self.user.id
            }
        )

    async def broadcast_status(self, event):
        """Получение статуса трансляции"""
        await self.send(json.dumps({
            'type': 'broadcast_status',
            'action': event['action'],
            'user_id': event['user_id'],
            'username': event.get('username'),
            'user_avatar': event.get('user_avatar'),
            'broadcast_type': event.get('broadcast_type', 'audio')
        }))

    async def mic_status(self, event):
        """Получение статуса микрофона ведущего"""
        await self.send(json.dumps({
            'type': 'mic_status',
            'enabled': event['enabled'],
            'user_id': event['user_id']
        }))

    async def cam_status(self, event):
        """Получение статуса камеры ведущего"""
        await self.send(json.dumps({
            'type': 'cam_status',
            'enabled': event['enabled'],
            'user_id': event['user_id']
        }))

    async def playlist_item(self, event):
        """Получение текущего элемента плейлиста"""
        await self.send(json.dumps({
            'type': 'playlist_item',
            'user_id': event['user_id'],
            'media_file': event['media_file']
        }))

    async def webrtc_offer(self, event):
        """Получение WebRTC offer от ведущего"""
        await self.send(json.dumps({
            'type': 'webrtc_offer',
            'offer': event['offer'],
            'user_id': event['user_id']
        }))

    async def webrtc_answer(self, event):
        """Получение WebRTC answer от ведущего"""
        await self.send(json.dumps({
            'type': 'webrtc_answer',
            'answer': event['answer']
        }))

    async def ice_candidate(self, event):
        """Получение ICE candidate"""
        await self.send(json.dumps({
            'type': 'ice_candidate',
            'candidate': event['candidate']
        }))

    async def new_message(self, event):
        """Получение нового сообщения"""
        await self.send(json.dumps({
            'type': 'new_message',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'username': event['username'],
            'content': event['content'],
            'created_at': event['created_at']
        }))

    async def send_active_broadcasts(self):
        """Отправить список активных трансляций"""
        broadcasts = await self.get_active_broadcasts()

        await self.send(json.dumps({
            'type': 'active_broadcasts',
            'broadcasts': broadcasts
        }))

    @sync_to_async
    def get_active_broadcasts(self):
        """Получить активные трансляции из БД"""
        from .models import Broadcast

        active_broadcasts = []
        broadcasts = Broadcast.objects.filter(is_active=True).select_related('user')

        for broadcast in broadcasts:
            active_broadcasts.append({
                'user_id': broadcast.user.id,
                'username': broadcast.user.username,
                'user_avatar': broadcast.user.username[0].upper(),
                'role': broadcast.user.role,
                'broadcast_type': 'video' if broadcast.cam_enabled else 'audio',
                'mic_enabled': broadcast.mic_enabled,
                'cam_enabled': broadcast.cam_enabled,
                'started_at': broadcast.started_at.strftime('%Y-%m-%d %H:%M')
            })

        return active_broadcasts

    @sync_to_async
    def get_broadcast_info(self, broadcaster_id):
        """Получить информацию о трансляции"""
        from .models import Broadcast

        try:
            broadcast = Broadcast.objects.get(user_id=broadcaster_id, is_active=True)

            return {
                'user_id': broadcast.user.id,
                'username': broadcast.user.username,
                'user_avatar': broadcast.user.username[0].upper(),
                'broadcast_type': 'video' if broadcast.cam_enabled else 'audio',
                'volume': broadcast.volume,
                'mic_enabled': broadcast.mic_enabled,
                'cam_enabled': broadcast.cam_enabled,
                'started_at': broadcast.started_at.strftime('%Y-%m-%d %H:%M')
            }
        except Broadcast.DoesNotExist:
            return None

    @sync_to_async
    def save_message(self, content):
        """Сохранить сообщение в БД"""
        from .models import Message
        from django.utils import timezone

        message = Message.objects.create(
            user=self.user,
            content=content,
            status='new'
        )

        return {
            'id': message.id,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M')
        }