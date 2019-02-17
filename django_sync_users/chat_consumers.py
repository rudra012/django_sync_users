# https://groups.google.com/forum/#!topic/django-developers/zfkk_nX3C5c

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.db.models import F
from django.utils import timezone

from chat.exceptions import ClientError
from chat.utils import get_room_or_error


class WsChatConsumer(AsyncJsonWebsocketConsumer):
    """
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

        # Store which rooms the user has joined on this connection
        self.rooms = set()
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

    async def receive_json(self, content, **kwargs):
        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """
        # Messages will have a "command" key we can switch on
        command = content.get("command", None)
        try:
            if command == "join":
                # Make them join the room
                await self.join_room(content["room"])
            elif command == "leave":
                # Leave the room
                await self.leave_room(content["room"])
            elif command == "send":
                await self.send_room(content["room"], content["message"])
        except ClientError as e:
            # Catch any errors and send it back
            await self.send_json({"error": e.code})

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

    async def join_room(self, room_name):
        """
        Called by receive_json when someone sent a join command.
        """
        # The logged-in user is in our scope thanks to the authentication ASGI middleware
        room = await get_room_or_error(room_name, self.scope["user"])
        # Send a join message if it's turned on
        if settings.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.join",
                    "room_id": room_name,
                    "username": self.scope["user"].username,
                }
            )
        # Store that we're in the room
        self.rooms.add(room_name)
        # Add them to the group so they get room messages
        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name,
        )
        # Instruct their client to finish opening the room
        await self.send_json({
            "join": room.room_name,
            "title": room.room_name,
        })

    async def leave_room(self, room_id):
        """
        Called by receive_json when someone sent a leave command.
        """
        # The logged-in user is in our scope thanks to the authentication ASGI middleware
        room = await get_room_or_error(room_id, self.scope["user"])
        # Send a leave message if it's turned on
        if settings.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.leave",
                    "room_id": room_id,
                    "username": self.scope["user"].username,
                }
            )
        # Remove that we're in the room
        self.rooms.discard(room_id)
        # Remove them from the group so they no longer get room messages
        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name,
        )
        # Instruct their client to finish closing the room
        await self.send_json({
            "leave": str(room.id),
        })

    async def send_room(self, room_id, message):
        """
        Called by receive_json when someone sends a message to a room.
        """
        # Check they are in this room
        if room_id not in self.rooms:
            raise ClientError("ROOM_ACCESS_DENIED")
        # Get the room and send to the group about it
        room = await get_room_or_error(room_id, self.scope["user"])
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.message",
                "room_id": room_id,
                "username": self.scope["user"].username,
                "message": message,
            }
        )
