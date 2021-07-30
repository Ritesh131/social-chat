from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from authentication.models import User
from stream_app.models import *
import json
from stream_app.serializer import StreamChatDetailSerializer


class StreamChatConsumer(WebsocketConsumer):
    # Called when WebSocket connection is established, ws://

    def connect(self, *args, **kwargs):
        uid = self.scope["url_route"]["kwargs"]["user"]
        ch = self.scope["url_route"]["kwargs"]["channel_name"]

        user = User.objects.get(pk=uid)
        stream = Stream.objects.get(channel_name=ch)

        self.room_name = user.username
        self.room_group_name = stream.title

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(
            json.dumps({'status': 'connection created successfully'})
        )

    def receive(self):
        pass

    def disconnect(self):
        print('disconnect call')
        self.disconnect()

    def send_message(self, event):
        stream_id = event['value']['stream']
        query = StreamChat.objects.filter(stream=stream_id).order_by('-id')
        serializer = StreamChatDetailSerializer(query, many=True)
        self.send(json.dumps(serializer.data))
