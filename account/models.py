from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    profile_pic = models.ImageField(upload_to='user_profile', null=True,
                                    blank=True, max_length=300)
    is_online = models.BooleanField(default=False)
    no_of_connection = models.PositiveIntegerField(default=0)
    last_online = models.DateTimeField('last online', blank=True, null=True)
