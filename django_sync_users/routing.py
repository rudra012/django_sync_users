# https://channels.readthedocs.io/en/latest/topics/routing.html
# from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter
from django.urls import path

from django_sync_users.chat_consumers import WsChatConsumer
from django_sync_users.token_auth import TokenAuthMiddlewareStack

# https://stackoverflow.com/questions/43392889/how-do-you-authenticate-a-websocket-with-token-authentication-on-django-channels
application = ProtocolTypeRouter({
    "websocket": TokenAuthMiddlewareStack(
        URLRouter([
            # URLRouter just takes standard Django path() or url() entries.
            path("ws_connect/", WsChatConsumer),
            # path("ws_connect/", WsConsumer),
        ]),
    ),
})
