import os
from django.core.asgi import get_asgi_application
from channels.routing import get_default_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
import django


# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django.setup()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')
application = get_asgi_application()


