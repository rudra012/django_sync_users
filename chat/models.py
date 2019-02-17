from django.db import models

from account.models import User
from base.models import TimeStampedModel


class Room(TimeStampedModel):
    """
    New channel created on Send bird
    """

    room_name = models.CharField(max_length=100, unique=True)

    # All channel members
    members_count = models.PositiveSmallIntegerField(default=0)
    members = models.ManyToManyField(User, related_name="room_members", through='RoomMember')

    # Last message for this channel
    last_message = models.TextField(default="", blank=True)

    # If only "staff" users are allowed (is_staff on django's User)
    staff_only = models.BooleanField(default=False)

    def __str__(self):
        return "{}-{}".format(self.id, self.room_name)


class RoomMember(TimeStampedModel):
    """
    All channel members invited in channel
    """
    channel = models.ForeignKey(Room, related_name="member_channel", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="member_user", on_delete=models.CASCADE,
        limit_choices_to={'is_staff': False, 'is_deleted': False},
    )

    def __str__(self):
        return "ChannelMember-{}-{}".format(self.id, self.user.full_name)
