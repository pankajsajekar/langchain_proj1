# ai_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'You are now connected to the chat server.'
        }))
        print("WebSocket connected")

    async def disconnect(self, close_code):
        # Handle disconnection
        print(f"WebSocket disconnected with code: {close_code}")

    async def receive(self, text_data):
        # Receive message from WebSocket
        try:
            data = json.loads(text_data)
            message = data.get('message', '')
            
            # Echo the message back to the client
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': f'Echo: {message}'
            }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))