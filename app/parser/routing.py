from django.urls import path

from .consumers import TestConsumer, ParsingStatusConsumer

ws_urlpatterns = [
    path('ws/test/', TestConsumer.as_asgi()),
    path('ws/notification/', ParsingStatusConsumer.as_asgi()),
]
