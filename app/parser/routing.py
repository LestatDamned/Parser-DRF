from django.urls import path

from .consumers import SimpleWebSocketConsumer, ParsingStatusConsumer

ws_urlpatterns = [
     path('ws/test/', SimpleWebSocketConsumer.as_asgi()),
     path('ws/notification/', ParsingStatusConsumer.as_asgi()),
]