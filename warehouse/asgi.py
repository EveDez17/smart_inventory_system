"""
ASGI config for warehouse project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import inventory.routing  # Replace 'your_app_name' with your actual app name

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warehouse.settings')  # Assuming 'warehouse' is your Django project name

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Django's ASGI application to handle traditional HTTP requests
    "websocket": AuthMiddlewareStack(  # WebSocket protocol
        URLRouter(
            inventory.routing.websocket_urlpatterns  # Use your app's WebSocket routing
        )
    ),
})

