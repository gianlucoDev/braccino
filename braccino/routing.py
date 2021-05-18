from django.urls import path

from braccio.consumers import BraccioConsumer

websocket_urlpatterns = [
    path('ws/braccio/<str:serial_number>/', BraccioConsumer.as_asgi()),
]
