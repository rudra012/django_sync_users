from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        headers = dict(scope['headers'])
        # print('origin', scope.get('origin'))
        # print('client', scope.get('client'))
        # print('type', scope.get('type'))
        # print('headers', headers)
        # print('query_string', scope.get('query_string'))
        if scope.get('query_string'):
            query_string = scope['query_string']
            # print(query_string)
            all_params = query_string.decode().split('&')
            # print(all_params)
            for param in all_params:
                if 'token' in param.lower():
                    token_name, token_key = param.split('=')
                    try:
                        if token_name.lower() == 'token':
                            token = Token.objects.get(key=token_key)
                            scope['user'] = token.user
                    except Exception as e:
                        print('Error: TokenAuthMiddleware: ', e)
                    break
        elif b'authorization' in headers:
            try:
                token_name, token_key = headers[b'authorization'].decode().split()
                if token_name == 'Token':
                    token = Token.objects.get(key=token_key)
                    scope['user'] = token.user
            except Token.DoesNotExist:
                scope['user'] = AnonymousUser()
        return self.inner(scope)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
