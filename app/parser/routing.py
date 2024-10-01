from django.urls import path

from .consumers import ParsingStatusConsumer

ws_urlpatterns = [
     path('ws/notification/', ParsingStatusConsumer.as_asgi()),
]