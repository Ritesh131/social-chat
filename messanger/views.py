from django.http.response import HttpResponse
from rest_framework import serializers
from .models import Message
from .serializers import MessageSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from authentication.models import User
from authentication.serializers import UserSerializer
from art_app.models import UserFollowers
from art_app.serializers import UserNotificationSerializer


def index(request):
    return HttpResponse('dndsn')


class MessageUser(APIView):

    def get(self, request, id):
        messages_query = Message.objects.filter(Q(sender=id) | Q(receiver=id)).order_by('-id')
        print('messages_query', messages_query)
        message_user = list(set([]))
        for i in messages_query:
            if (int(i.sender.id) != int(id)) or (int(i.receiver.id) != int(id)):
                message_user.append(i.sender.id)
                message_user.append(i.receiver.id)
        recent_message_user = User.objects.filter(id__in=message_user)
        serializer = UserSerializer(recent_message_user, many=True)
        # Friend list
        query = UserFollowers.objects.filter(Q(following_user_id=id) | Q(user_id=id)).exclude(id__in=message_user)
        following_id = list(set([]))
        for i in query:
            following_id.append(i.user_id.id)
            following_id.append(i.following_user_id.id)
        friend_user = UserSerializer(following_id, many=True)
        return Response({'message_user': serializer.data, 'friend_user': friend_user.data})


class MessageView(APIView):

    def get(self, request, user, friend):
        messages = Message.objects.filter(Q(sender__in=[user, friend]), Q(receiver__in=[user, friend])).order_by('-id')
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            query_sender = User.objects.get(pk=request.data['sender'])
            query_receiver = User.objects.get(pk=request.data['receiver'])
            try:
                msg = request.data['message']
                message = f'{query_sender.first_name} {query_sender.last_name} sent you a message: {msg}.'
                notice_user = request.data['receiver']
                notice = {
                    'notice_user': notice_user,
                    'message': message
                }
                response_notice = UserNotificationSerializer(data=notice)
                if response_notice.is_valid():
                    response_notice.save()
                print(response_notice)
            except Exception as e:
                pass
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
