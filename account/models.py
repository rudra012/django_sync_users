from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    profile_pic = models.ImageField(upload_to='user_profile', null=True,
                                    blank=True, max_length=300)
