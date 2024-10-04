"""
ASGI config for ParserdjangoProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from parser.channelsmiddleware import jwt_auth_middleware
from parser.routing import ws_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ParserdjangoProject.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': jwt_auth_middleware(
            URLRouter(ws_urlpatterns)
        ),
})
# application = ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': AuthMiddlewareStack(
#             URLRouter(ws_urlpatterns)
#         ),
# })


