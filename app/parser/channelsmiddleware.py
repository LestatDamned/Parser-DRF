import logging

import jwt
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger("ParserdjangoProject")
User = get_user_model()


class JWTAuthMiddleware:
    """
    Middleware для аутентификации WebSocket с использованием JWT.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Проверяем наличие заголовка Authorization
        headers = dict(scope['headers'])
        auth_header = headers.get(b'authorization')

        logger.info(f' Headers: {headers}')

        if auth_header is not None:
            # Получаем токен из заголовка
            token = auth_header.decode().split()[1]  # Bearer <token>
            logger.info(f' Token: {token}')
            try:
                # Проверяем и декодируем токен
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                logger.info(f'Decoded payload: {payload}')
                user = await database_sync_to_async(User.objects.get)(id=payload['user_id'])
                logger.info(f' User: {user}')
            except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist) as e:
                logger.error(f' Error: {e}')
                user = AnonymousUser()
        else:
            user = AnonymousUser()

        # Добавляем пользователя в scope
        scope['user'] = user
        return await self.inner(scope, receive, send)


# Используй этот middleware вместе с AuthMiddlewareStack
def jwt_auth_middleware(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
