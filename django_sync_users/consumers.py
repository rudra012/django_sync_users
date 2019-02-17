# https://groups.google.com/forum/#!topic/django-developers/zfkk_nX3C5c

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db.models import F
from django.utils import timezone


class WsConsumer(AsyncJsonWebsocketConsumer):
    """
    This chat consumer handles websocket connections for chat clients.

    It uses AsyncJsonWebsocketConsumer, which means all the handling functions
    must be async functions, and any sync work (like ORM access) has to be
    behind database_sync_to_async or sync_to_async. For more, read
    http://channels.readthedocs.io/en/latest/topics/consumers.html

    pprint(self.scope)
        '''
        {'client': ['127.0.0.1', 60140],
         'cookies': {},
         'headers': [(b'host', b'localhost:8000'),
                     (b'connection', b'Upgrade'),
                     (b'pragma', b'no-cache'),
                     (b'cache-control', b'no-cache'),
                     (b'upgrade', b'websocket'),
                     (b'origin', b'https://www.websocket.org'),
                     (b'sec-websocket-version', b'13'),
                     (b'user-agent',
                      b'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, l'
                      b'ike Gecko) Chrome/72.0.3626.96 Safari/537.36'),
                     (b'accept-encoding', b'gzip, deflate, br'),
                     (b'accept-language', b'en-US,en;q=0.9,ms;q=0.8'),
                     (b'sec-websocket-key', b'Yjb05HlCNDoj2HXYBfXO1g=='),
                     (b'sec-websocket-extensions',
                      b'permessage-deflate; client_max_window_bits')],
         'path': '/ws_connect/',
         'path_remaining': '',
         'query_string': b'encoding=text',
         'server': ['127.0.0.1', 8000],
         'session': <django.utils.functional.LazyObject object at 0x7f2035b3a3c8>,
         'subprotocols': [],
         'type': 'websocket',
         'url_route': {'args': (), 'kwargs': {}},
         'user': <channels.auth.UserLazyObject object at 0x7f2035b3a438>}
        '''
        pprint(dir(self))
        '''
        ['accept', 'base_send', 'channel_layer', 'channel_layer_alias', 'channel_name', 'channel_receive',
         'close', 'connect', 'decode_json', 'disconnect', 'dispatch', 'encode_json', 'groups', 'receive',
         'receive_json', 'scope', 'send', 'send_json', 'websocket_connect', 'websocket_disconnect',
         'websocket_receive']
        '''
    """
    # Create on group
    group_name = 'global'

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.

        To send to a single channel, just find its channel name (for the example above, we could crawl the database),
        and use channel_layer.send:
        https://channels.readthedocs.io/en/latest/topics/channel_layers.html
        """
        user = self.scope.get("user")
        print('WS: connect', user)
        # print(self.group_name, self.channel_name)
        # print(self.channel_layer, self.channel_layer_alias)
        # Accept the connection
        if user.is_anonymous:
            # Reject the connection
            await self.close()
        else:
            # Accept the connection
            await self.accept()
        user.no_of_connection = F('no_of_connection') + 1
        user.is_online = True
        user.save()

        # Add user to Group
        await self.channel_layer.group_add('user_channel_{}'.format(user.id), self.channel_name)
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Send message is group so all channels in that group will get message
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        await channel_layer.group_send(self.group_name, {
            "type": "chat.join",
            "text": "Hello there!",
        })

        # # To send message in single channel
        # from channels.layers import get_channel_layer
        #
        # channel_layer = get_channel_layer()
        # await channel_layer.send(self.channel_name, {
        #     "type": "chat.join",
        #     "text": "Hello there!",
        # })

    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        user = self.scope.get("user")
        print('WS: disconnect', user)
        await self.channel_layer.group_discard('user_channel_{}'.format(user.id), self.channel_name)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        user.no_of_connection = F('no_of_connection') - 1
        user.last_online = timezone.now()
        user.save()

        # https://simpleisbetterthancomplex.com/tips/2016/08/23/django-tip-13-f-expressions.html
        user.refresh_from_db()
        save_data = False
        if user.no_of_connection < 0:
            user.no_of_connection = 0
            save_data = True
        if not user.no_of_connection:
            user.is_online = False
            save_data = True
        if save_data:
            user.save()

    # ####### Handlers for messages sent over the channel layer #######

    # These helper methods are named by the types we send - so chat.join becomes chat_join
    async def chat_join(self, event):
        """
        Called when someone has joined our chat.
        """
        # Send a message down to the client
        await self.send_json(
            {
                # "msg_type": settings.MSG_TYPE_ENTER,
                "room": 'test',
            },
        )
