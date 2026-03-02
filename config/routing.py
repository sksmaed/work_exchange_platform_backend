from django.urls import path

from config import consumers
from features.chat.consumers import ChatConsumer

websocket_urlpatterns = [
    path("ws/notify/", consumers.NotificationConsumer.as_asgi()),
    path("ws/chat/<str:conversation_id>/", ChatConsumer.as_asgi()),
]
