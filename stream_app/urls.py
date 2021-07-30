from django.urls import path
from .views import *

urlpatterns = [
    path('token/genrate', StreamTokenView.as_view()),
    path('list', StreamView.as_view()),
    path('delete/<int:id>', StreamView.as_view()),
    path('channel/<channel_name>', GetTokenView.as_view()),
    path('update', UpdateStream.as_view()),
    path('user/<int:pk>', UserStreamView.as_view()),
    path('pay/stream', PayStreamView.as_view()),
    path('event', PaidStream.as_view()),
    path('user/auth/<stream>', CheckUserStreamPermission.as_view()),
    path('chat/send', ChatSendView.as_view()),
]
