import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import get_default_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
import example.routing
from example.routing import websocket_urlpatterns




# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')
application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            example.routing.websocket_urlpatterns
        )
    ),
})
#application = get_asgi_application()


