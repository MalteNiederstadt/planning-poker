import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')

import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import get_default_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
import example.routing
django_asgi_app = get_asgi_application()
from planning_poker.consumers import PokerConsumer

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.


#application = get_asgi_application()
#application = get_default_application()

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    # WebSocket chat handler
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path("example/admin/", PokerConsumer.as_asgi()),
                path("example/", PokerConsumer.as_asgi()),
            ])
        )
    ),
})