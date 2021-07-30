"""
ASGI config for liveChat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from stream_app.consumers import StreamChatConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'users.settings')

application = get_asgi_application()

ws_patterns = [
    path('ws/chat/<int:user>/<str:channel_name>', StreamChatConsumer.as_asgi())
]

application = ProtocolTypeRouter({
    'websocket': URLRouter(ws_patterns)
})
