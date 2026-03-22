# player/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/broadcast/', consumers.BroadcastConsumer.as_asgi()),
    path('ws/stream/', consumers.StreamConsumer.as_asgi()),
]