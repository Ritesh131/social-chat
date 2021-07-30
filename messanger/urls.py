from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index),
    path('api/messages/<int:user>/<int:friend>', MessageView.as_view(), name='message-detail'),
    path('api/messages/', MessageView.as_view(), name='message-save'),
    path('api/message/user/<int:id>', MessageUser.as_view())
]