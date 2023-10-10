from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import planning_poker.routing
from django.urls import re_path
from planning_poker.consumers import consumers

websocket_urlpatterns = [
    re_path(r'ws/.*$', consumers.JsonWebsocketConsumer.as_asgi()),  # Wildcard path for all WebSocket connections
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(planning_poker.routing.websocket_urlpatterns)),
})

