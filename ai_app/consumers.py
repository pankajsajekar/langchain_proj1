# ai_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth.models import User
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from ai_app.models import AIChats
from ai_app.handler.llm_service import SimpleLLMHandler
from django.conf import settings


openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)

@database_sync_to_async
def save_chat_message(user, message, response, tokens_used=0):
    chat_message = AIChats(user=user, message=message, response=response, tokens_used=tokens_used)
    chat_message.save()
    return chat_message


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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize instance variables
        self.user = None
        self.jwt_token = None

        # Initialize LLM handler (adjust API key source as needed)
        if openai_api_key:
            self.llm_handler = SimpleLLMHandler(api_key=openai_api_key)
        else:
            self.llm_handler = None  # Handle missing key gracefully

    async def connect(self):
        # Extract query parameters
        query_string = self.scope.get('query_string', b'').decode()
        params = parse_qs(query_string)

        # Get token
        self.jwt_token = params.get('token', [None])[0]

        if not self.jwt_token:
            await self.close(code=4001)
            return

        self.user = await get_user_from_token(self.jwt_token)
        
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

        # Clear memory on disconnect
        if hasattr(self, 'llm_handler'):
            self.llm_handler.clear_history()


    async def receive(self, text_data):
        # Receive message from WebSocket
        try:
            data = json.loads(text_data)
            message = data.get('message', '')

            await self.send(text_data=json.dumps({
                'type': 'status',
                'message': '🤔 Thinking...'
            }))
            
            if self.llm_handler:
                # Get LLM response
                response, tokens_used = await self.llm_handler.get_response(message)
                print(f"LLM response: {response}")

                await self.send(text_data=json.dumps({
                    'type': '<STARTOFTURN>',
                    'message': ''
                }))

                # Stream the response
                async for chunk in self.llm_handler.stream_response(response, chunk_size=3):
                    await self.send(text_data=json.dumps({
                        'type': 'chat_response_stream',
                        'message': chunk
                    }))

                # Send stream end marker
                await self.send(text_data=json.dumps({
                    'type': '<ENDOFTURN>',
                    'message': '',
                }))

                # Save chat message
                # await save_chat_message(self.user, message, response, tokens_used)

            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'LLM not configured.'
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))