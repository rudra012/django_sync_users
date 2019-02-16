# https://channels.readthedocs.io/en/latest/topics/routing.html
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter
from django.urls import path

from django_sync_users.consumers import WsConsumer

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # URLRouter just takes standard Django path() or url() entries.
            path("ws_connect/", WsConsumer),
        ]),
    ),
})
