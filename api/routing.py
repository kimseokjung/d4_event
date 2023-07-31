from django.urls import path, re_path
from api import consumers

websocket_urlpatterns = [
    re_path(r'ws/countdown/', consumers.CountdownConsumer.as_asgi())
],
