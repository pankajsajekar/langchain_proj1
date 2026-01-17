from django.urls import re_path

from ai_app.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ai/chat/$', ChatConsumer.as_asgi()),
]
