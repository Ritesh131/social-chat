from rest_framework import serializers
from stream_app.models import *

class StreamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stream
        fields = '__all__'


class StreamTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = StreamToken
        fields = '__all__'


class StreamChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = StreamChat
        fields = '__all__'


class UserNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

class StreamChatDetailSerializer(serializers.ModelSerializer):
    user = UserNameSerializer()

    class Meta:
        model = StreamChat
        fields = '__all__'
