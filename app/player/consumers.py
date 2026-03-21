import json
from channels.generic.websocket import AsyncWebsocketConsumer


class BroadcastConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'broadcast'
        self.room_group_name = f'stream_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'signal',
                'data': data
            }
        )

    async def signal(self, event):
        await self.send(text_data=json.dumps(event['data']))


class StreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'broadcast'
        self.room_group_name = f'stream_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def signal(self, event):
        await self.send(text_data=json.dumps(event['data']))