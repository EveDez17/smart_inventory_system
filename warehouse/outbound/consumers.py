import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from warehouse.outbound.models import VNATask


logger = logging.getLogger(__name__)

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        
        # Simulate fetching the latest task for demonstration; adapt as necessary.
        task = await self.get_latest_task()
        if task:
            message = {
                "type": "new_task",
                "task_id": str(task.id),  # Dynamic task_id from the database
                "message": "New VNA task assigned."
            }
        else:
            message = {
                "type": "error",
                "message": "No tasks available."
            }
        await self.send(text_data=json.dumps(message))

    async def disconnect(self, close_code):
        logger.info(f"Disconnected with close code {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message')
            if message:
                # Echoing back the received message
                await self.send(text_data=json.dumps({
                    'message': message
                }))
            else:
                logger.error("No message found in received data")
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from received data")

    @database_sync_to_async
    def get_latest_task(self):
        # Fetch the latest task; modify query as needed for your logic.
        return VNATask.objects.order_by('-id').first()
