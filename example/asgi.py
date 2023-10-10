import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')

import django
django.setup()

#from django.core.asgi import get_asgi_application
from channels.routing import get_default_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path


# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.


#application = get_asgi_application()
#application = get_default_application()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})