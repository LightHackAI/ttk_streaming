import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BroadcastConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Получаем broadcast_id из URL
        self.broadcast_id = self.scope['url_route']['kwargs'].get('broadcast_id', 'default')
        self.room_group_name = f'broadcast_{self.broadcast_id}'
        
        print(f"🔌 WebSocket connect: broadcast_id={self.broadcast_id}")
        print(f"📡 Room group: {self.room_group_name}")
        
        # Добавляем в группу
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Принимаем соединение
        await self.accept()
        print(f"✅ WebSocket соединение ПРИНЯТО для {self.broadcast_id}")
        
        # Отправляем приветственное сообщение
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'broadcast_id': self.broadcast_id,
            'message': 'WebSocket connected successfully!'
        }))
        
        print(f"📤 Отправлено приветственное сообщение")
    
    async def disconnect(self, close_code):
        print(f"🔌 WebSocket disconnect: broadcast_id={self.broadcast_id}, code={close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        print(f"📨 Получено сообщение от {self.broadcast_id}: {text_data}")
        try:
            data = json.loads(text_data)
            
            # Пересылаем сообщение всем в группе
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_message',
                    'message': data,
                    'sender_channel': self.channel_name
                }
            )
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")
    
    async def broadcast_message(self, event):
        """Отправляет сообщение всем в группе"""
        # Не отправляем обратно отправителю
        if event['sender_channel'] != self.channel_name:
            print(f"📤 Отправка сообщения клиенту {self.broadcast_id}")
            await self.send(text_data=json.dumps(event['message']))
    
    async def user_joined(self, event):
        """Пользователь присоединился"""
        print(f"👤 Пользователь присоединился: {event}")
        await self.send(text_data=json.dumps({
            'type': 'user-joined',
            'user_id': event.get('user_id'),
            'username': event.get('username')
        }))