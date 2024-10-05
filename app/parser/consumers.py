import json

from celery.result import AsyncResult
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
        await self.close()
        # await self.channel_layer.group_discard(
        #     self.group_name,
        #     self.channel_name,
        # )

    async def parsing_status(self, event):
        status = event['status']
        task_id = event['task_id']
        result_id = event['result_id']
        await self.send(text_data=json.dumps({
            'status': status,
            "task_id": task_id,
            "result_id": result_id,
        }))

    async def percent_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
        }))
        # task_result = AsyncResult(task_id)
        # if task_result.state == 'PARSING':
        #     await self.send(text_data=json.dumps({
        #         "progress": "10%",
        #         "status": task_result.state,
        #     }
        #     ))
        #
        # elif task_result.state == "PROGRESS":
        #     progress = task_result.info
        #     current = progress.get('number', 0)
        #     total = progress.get('total', 1)
        #     await self.send(text_data=json.dumps({
        #         "progress": current/total,
        #         "status": status,
        #     }))
        # else:
        #     await self.send(text_data=json.dumps({
        #         'status': task_result,
        #         'task_id': task_id,
        #         'result_id': result_id
        #     }))


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
