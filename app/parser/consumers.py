import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ParsingStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        self.group_name = f'user_{self.user.id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
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