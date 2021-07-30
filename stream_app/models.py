from django.db import models
from authentication.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

# Create your models here.
class Stream(models.Model):
    STREAM_TYPE = (
        ('free', 'free'),
        ('premium', 'premium')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(choices=STREAM_TYPE, default='free', max_length=15)
    stream_cost = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=150, default='')
    description = models.TextField(max_length=1500, default='', null=True, blank=True)
    thumbnil = models.FileField(null=True, blank=True)
    channel_name = models.CharField(max_length=200, default='', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateField(auto_now=True)


class StreamToken(models.Model):
    channel_name = models.CharField(max_length=200, default='', null=True, blank=True)
    token = models.CharField(max_length=200, default='', null=True, blank=True)
    date_created = models.DateField(auto_now=True)


class StreamSubcribe(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class StreamChat(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=500, default='', null=True, blank=True)
    date_created = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        data = {
            'username': self.user.username,
            'message': self.message,
            'stream': self.stream.id,
            'name': self.stream.user.first_name + ' ' + self.stream.user.last_name
        }


        async_to_sync(channel_layer.group_send)(
            f'{self.stream.title}', {
                'type': 'send_message',
                'value': data,
            }
            )
        super(StreamChat, self).save(*args, **kwargs)