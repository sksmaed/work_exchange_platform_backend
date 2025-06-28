from django.urls import path

from config import consumers

websocket_urlpatterns = [
    path("ws/notify/", consumers.NotificationConsumer.as_asgi()),
]
