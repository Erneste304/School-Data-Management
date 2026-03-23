import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rutabo_school.settings')

# Standard Django ASGI application for HTTP
django_asgi_app = get_asgi_application()

# Import WebSocket URL patterns after Django setup
# (These will be created in Step 5 when we build chat & livestream)
try:
    from accounts.routing import websocket_urlpatterns
except ImportError:
    websocket_urlpatterns = []

application = ProtocolTypeRouter({
    # HTTP → standard Django views
    'http': django_asgi_app,

    # WebSocket → Django Channels with auth
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})