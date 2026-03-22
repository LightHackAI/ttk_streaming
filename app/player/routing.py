from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/broadcast/(?P<broadcast_id>\w+)/$', consumers.BroadcastConsumer.as_asgi()),
    re_path(r'ws/broadcast/$', consumers.BroadcastConsumer.as_asgi()),
]