import os
import re
import sys
import time
import random
from django.db.models import query
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from users import settings
from src.RtcTokenBuilder import *
from .serializer import *
from .models import *
from payment_app.serializer import *
from payment_app.models import *
from payment_app.views import *
from art_app.serializers import *
import stripe

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create your views here.
class StreamTokenView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        query = Stream.objects.filter(user=request.user, is_active=True).order_by('-id')
        serializer = StreamSerializer(query, many=True)
        return Response(serializer.data)

    def post(self, request):
        appID = settings.AGORA_APP_ID
        appCertificate = settings.AGORA_APP_CERTIFICATE       
        uid = 0
        userAccount = request.user.pk
        expireTimeInSeconds = 900000
        currentTimestamp = int(time.time())
        privilegeExpiredTs = currentTimestamp + expireTimeInSeconds
        channelName = str(random.randint(100, 999)) + request.user.username[::-1] + str(request.user.pk) + str(privilegeExpiredTs)
        token = RtcTokenBuilder.buildTokenWithUid(appID, appCertificate, channelName, uid, Role_Attendee, privilegeExpiredTs)        
        context = {
            'token':token,
            'channelName':channelName,
        }
        payload = request.data.copy()
        payload['user'] = request.user.pk
        payload['channel_name'] = channelName
        serializer = StreamSerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
        try:
            StreamToken.objects.create(channel_name=channelName, token=token)
        except:
            pass
        data = serializer.data
        data['token'] = token
        data['channelName'] = channelName
        return Response(data)


class StreamView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        query = Stream.objects.filter(is_active=True, type='free').order_by('-id')
        serializer = StreamSerializer(query, many=True)
        return Response(serializer.data)

    def delete(self, request, id):
        query = Stream.objects.filter(pk=id).delete()
        return Response('deleted')


class GetTokenView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, channel_name):
        query = StreamToken.objects.filter(channel_name=channel_name).last()
        query_stream = Stream.objects.filter(channel_name=channel_name).last()
        serializer_token = StreamTokenSerializer(query)
        serializer_stream = StreamSerializer(query_stream)
        return Response({'token':serializer_token.data, 'stream':serializer_stream.data})

    def put(self, request, channel_name):
        query = Stream.objects.filter(channel_name=channel_name).update(is_active=False)
        return Response('live  end')


class UpdateStream(APIView):
    def put(self, request):
        query = Stream.objects.get(pk=request.data['stream'])
        serializer = StreamSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


class UserStreamView(APIView):
    def get(self, request, pk):
        query = Stream.objects.filter(user=pk).order_by('-id')
        serializer = StreamSerializer(query, many=True)
        return Response(serializer.data)


class PaidStream(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        query = Stream.objects.filter(is_active=True, type='premium').order_by('-id')
        print(query)
        serializer = StreamSerializer(query, many=True)
        return Response(serializer.data)


class CheckUserStreamPermission(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, stream):
        query = StreamSubcribe.objects.filter(user=request.user, stream__channel_name=stream)
        free_stream = Stream.objects.get(channel_name=stream)
        print(query)

        if free_stream.type == 'free':
            ctx = {'message':'User can access this live stream.', 'blob':True}
            return Response(ctx)
        query_len = len(query)
        if query_len < 1:            
            ctx = {'message':'User is not authorized for this call.', 'blob':False}
            return Response(ctx)
        ctx = {'message':'User can access this live stream.', 'blob':True}
        return Response(ctx)


class PayStreamView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        query = Stream.objects.get(id=request.data['stream'])
        exp_month = request.data['expiry'][0:2]
        exp_year = request.data['expiry'][3:5]
        amount_sent = query.stream_cost*100
        account = stripe.Token.create(
            card={
                "number": request.data['cardNumber'],
                "exp_month": exp_month,
                "exp_year": exp_year,
                "cvc": request.data['cvc'],
            },
        )
        if account.id:
            charge_create = stripe.Charge.create(
                amount=amount_sent,
                currency="usd",
                source=account.id,
                description="My First Test Charge (created for API)",
            )
            payment_data = {}
            payment_data['payment_from'] = request.user.id
            payment_data['payment_to'] = query.user.id
            payment_data['amount'] = query.stream_cost
            payment_data['transaction_id'] = account.id
            serializer = PaymentHistorySerializer(data=payment_data)
            if serializer.is_valid():
                serializer.save()
                print(serializer.data)
            try:
                res_payout = payout_artist(
                    query.user.id, query.stream_cost)
                print('res_payout', res_payout)
            except Exception as e:
                print('payout not done', e)
            
            try:
                paid = StreamSubcribe.objects.create(stream=query, user=request.user)
            except Exception as e:
                print(e)
            
            try:
                user = User.objects.get(id=query.user.id)
                message = f'{user.first_name} {user.last_name} is paid ${query.stream_cost} for your live stream - {query.title}.'
                notice_user = query.user.id
                notice = {
                    'notice_user': notice_user,
                    'message': message
                }
                response_notice = UserNotificationSerializer(data=notice)
                if response_notice.is_valid():
                    response_notice.save()
                print(response_notice.errors)
            except Exception as e:
                print(e)

            return Response({'stripe_res': charge_create})
        return Response({'message': account}, status=status.HTTP_400_BAD_REQUEST) 


class ChatSendView(APIView):
    def post(self, request):
        serializer = StreamChatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)