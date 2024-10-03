import json

from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer


class ParsingStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        self.group_name = f'user_{self.user.id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def parsing_status(self, event):
        status = event['status']
        task_id = event['task_id']
        result_id = event['result_id']

        await self.send(text_data=json.dumps({
            'status': status,
            'task_id': task_id,
            'result_id': result_id
        }))


from channels.generic.websocket import WebsocketConsumer

class SimpleWebSocketConsumer(WebsocketConsumer):
    def connect(self):
        if self.scope['user'].is_authenticated:
            self.accept()
        else:
            self.close()  # Закрываем соединение, если пользователь не аутентифицирован

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', 'No message')
        self.send(text_data=json.dumps({'message': f'You said: {message}'}))
