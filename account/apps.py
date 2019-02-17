import sys

from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'account'

    def ready(self):
        # print(sys.argv)
        if 'runserver' not in sys.argv:
            return True

        # Project Startup code
        from .models import User
        # Make all users offline and they were disconnected on restart of the system
        User.objects.all().update(is_online=False, no_of_connection=0)

        # Same if all clients are disconnected then no use of old channel in redis DB
        # So clearing all group channels
        import redis
        redis_client = redis.Redis('127.0.0.1')
        for key in redis_client.scan_iter(b'asgi::group:*'):
            redis_client.delete(key)
        # redis_client.delete(b'asgi::group:global')
        # startup code here
