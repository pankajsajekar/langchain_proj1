# ai_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth.models import User
from urllib.parse import parse_qs
from channels.db import database_sync_to_async

def validate_jwt_token(token_string):
    # Implement JWT token validation logic here
    try:
        token = AccessToken(token_string)
        user_id = token['user_id']
        return True, user_id
    except (TokenError, InvalidToken):
        return False, None

@database_sync_to_async
def get_user_from_token(token_string):
    is_valid, user_id = validate_jwt_token(token_string)
    if is_valid:
        # Fetch user from database using user_id
        try:
            user = User.objects.get(id=user_id)
            print(f"Authenticated user: {user.username}")
            return user
        except User.DoesNotExist:
            return None
    return None


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Extract query parameters
        query_string = self.scope.get('query_string', b'').decode()
        params = parse_qs(query_string)

        # Get token
        self.token = params.get('token', [None])[0]
        print(f"Received token: {self.token}")
        
        if not self.token:
            await self.close(code=4001)
            return
        
        self.user = await get_user_from_token(self.token)
        
        if not self.user:
            await self.close(code=4001)  # Unauthorized
            return

        print(f"User authenticated: {self.user.username}")

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