from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.models import *
from django.core.mail import send_mail
from users import settings
from .serializers import *
import random

class OTPView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        user = User.objects.filter(email=request.data['email']).last()
        if user:
            otp = random.randint(1111, 9999)
            try:
                subject = 'Inkster'
                message = f'Hi {user.username}, Here is OTP from Inkster.\n{otp}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email, ]
                send_mail(subject, message, email_from, recipient_list)
            except Exception as e:
                print('email not send.', e)
            model_data = request.data.copy()
            model_data['otp'] = otp
            model_data['user'] = user.pk
            serializer = OTPSerializer(data=model_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        return Response({'message':'There is no user register with this email.'})

    def put(self, request):
        user = User.objects.filter(email=request.data['email']).last()
        if user:
            query_otp = Otp.objects.filter(user=user.id).last()
            if query_otp:
                query_data = {
                    'verify': 'true'
                }
                if int(request.data['otp']) == int(query_otp.otp):
                    query_update = OTPSerializer(query_otp, data=query_data)
                    if query_update.is_valid():
                        query_update.save()
                        query = User.objects.get(id=query_update.data['user'])
                        data = {
                            'username': query.username,
                            'id': query.id
                        }
                        return Response({'message':'you have successfully verify OTP.', 'data':data}, status=status.HTTP_200_OK)
                    return Response({'message': query_update.errors}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'message': 'OTP that you enter is not valid.', 'status': 400}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Please send OTP first.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'There is no user register with this email.'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    permission_classes = (permissions.AllowAny,)

    def put(self, request):
        user = User.objects.filter(email=request.data['email']).last()
        if user:
            query_otp = Otp.objects.filter(user=user.id, verify='true').last()
            if query_otp:
                user.set_password(request.data['password'])
                user.save()
                return Response({'message': 'You have successfully reset your password.'}, status=status.HTTP_200_OK)
            return Response({'message': 'First Verify OTP then reset your password'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'There is no user register with this email.'}, status=status.HTTP_400_BAD_REQUEST)
