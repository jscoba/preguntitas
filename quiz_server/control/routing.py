from django.urls import path

from . import consumers as ControlConsumer
from player import consumers as PlayerConsumer


websocket_urlpatterns = [
    path('ws/consumer_control/', ControlConsumer.ControlConsumer.as_asgi()),
    path('ws/consumer_player/', PlayerConsumer.PlayerConsumer.as_asgi()),
]