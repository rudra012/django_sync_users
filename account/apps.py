import sys

from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'account'

    def ready(self):
        # print(sys.argv)
        if 'runserver' not in sys.argv:
            return True
        # you must import your modules here
        # to avoid AppRegistryNotReady exception
        from .models import User
        User.objects.all().update(is_online=False, no_of_connection=0)
        # startup code here
