import json
from channels.generic.websocket import AsyncWebsocketConsumer

class UpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'global_updates'

        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Отключаемся от группы
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Получение сообщения от группы (из Signals)
    async def event_update(self, event):
        # Отправляем сообщение клиенту через WebSocket
        await self.send(text_data=json.dumps({
            'type': event['event_type'], # например: scoreboard_refresh
            'message': event.get('message', '')
        }))