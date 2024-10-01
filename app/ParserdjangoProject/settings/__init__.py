from ParserdjangoProject.settings.default_settings import *

DATABASES = {
    "default": {
        "ENGINE": str(os.getenv("SQL_ENGINE")),
        "NAME": str(os.getenv("SQL_DATABASE")),
        "USER": str(os.getenv("SQL_USER")),
        "PASSWORD": str(os.getenv("SQL_PASSWORD")),
        "HOST": str(os.getenv("SQL_HOST")),
        "PORT": str(os.getenv("SQL_PORT")),
    }
}

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'


CACHES = {
    'default': {
        'BACKEND': "django.core.cache.backends.redis.RedisCache",
        'LOCATION': "redis://127.0.0.1:6379/1",
    }
}
