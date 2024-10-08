import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ParsingStatusConsumer(AsyncWebsocketConsumer):
    """Класс для передачи сообщений по Websocket"""

    async def connect(self):
        self.user = self.scope['user']

        self.group_name = f'user_{self.user.id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': f'WebSocket connection established! User: {self.user}, Group: {self.group_name}'
        }))

    async def disconnect(self, close_code):
        await self.close()

    async def parsing_status(self, event):
        """Отправка сообщения о статусе парсинга"""

        status = event['status']
        task_id = event['task_id']
        result_id = event['result_id']
        await self.send(text_data=json.dumps({
            'status': status,
            "task_id": task_id,
            "result_id": result_id,
        }))

    async def percent_message(self, event):
        """Отправка сообщения о прессе парсинга в процентах"""

        message = event['message']
        await self.send(text_data=json.dumps({
            'progress': message,
        }))


class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': 'WebSocket connection established!'
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({
            'message': 'Received your message!'
        }))
