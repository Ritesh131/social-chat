from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import viewsets
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.filters import SearchFilter

from authentication.models import User, Country, UserLastSeenLog, PhoneNumberOtp, generate_otp_for_reset, UserOtp
from authentication.serializers import *
from token_storage.token_store import RemoteTokenStorage
from notification.notification import Notification
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action, api_view
import requests
from rest_framework.permissions import IsAuthenticated
from random import randint
from contacts.models import Contact
from contacts.views import FriendPost
from django.core.mail import send_mail
from users import settings
import random
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

class Countries(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = ()


class UserRegister(generics.CreateAPIView, generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = ()

    def perform_create(self, serializer):
        serializer.validated_data['is_active'] = True
        user = serializer.save()
        UserLastSeenLog.objects.create(user=user, status=0)

        try:
            otp = random.randint(1111, 9999)
            model_data = {}
            model_data['otp'] = otp
            model_data['user'] = user.id
            model_data['type'] = 'register'
            serializer = OTPSerializer(data=model_data)
            if serializer.is_valid():
                serializer.save()

            subject = 'Support Inkster'
            # message = f'Hi {user.username}, \nWelcome to Inkster! You are successfully registered.\n\n\tTeam Inkster'
            # email_from = settings.EMAIL_HOST_USER
            # recipient_list = [user.email, ]
            # send_mail(subject, message, email_from, recipient_list)

            merge_data = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'username': user.username,
                'otp': otp,
            }

            subject, from_email, to = 'Support Inkster', settings.EMAIL_HOST_USER, user.email
            html_body = render_to_string("inkster.html", merge_data)
            msg = EmailMultiAlternatives(subject=subject, from_email=from_email,
                             to=[to], body=html_body)
            msg.attach_alternative(html_body, "text/html")
            msg.send()
        except Exception as e:
            print('email not send.', e)

        # try:
        #     otp = random.randint(1111, 9999)
        #     subject = 'Support Inkster'
        #     message = f'Hi {user.username}, \n\tHere is your verification code from Inkster. {otp}\n\n\tTeam Inkster'
        #     email_from = settings.EMAIL_HOST_USER
        #     recipient_list = [user.email, ]
        #     send_mail(subject, message, email_from, recipient_list)
        #     model_data = {}
        #     model_data['otp'] = otp
        #     model_data['user'] = user.id
        #     model_data['type'] = 'register'
        #     serializer = OTPSerializer(data=model_data)
        #     if serializer.is_valid():
        #         serializer.save()
        # except Exception as e:
        #     print('email not send.', e)

        # Publish notification to notification service
        # notification = Notification()
        # notification.publish(
        #     'You are successfully registered on Social Exchange app',
        #     user.email, user.id, notification.TYPE_EMAIL,
        #     notification.EVENT_CONTACT_INVITE
        # )
        # update_contacts = Contact.objects.filter(
        #     mobile_no=user.phone_code + user.phone)
        # otp_helper(country_code=user.phone_code,
        #            phone=user.phone, email=user.email)
        # if update_contacts is not None:
        #     update_contacts.update(registered_id=user.id, is_registered=True)
        return serializer.data


class UserUpdate(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = (IsAuthenticated,)


class UserOtpViewSet(viewsets.ModelViewSet):
    serializer_class = UserOtpSerializer
    queryset = User.objects.all()

    def create(self, request):
        # this is use to check valid otp and activating user account
        otp = UserOtp.objects.filter(
            user__email__exact=self.request.data.get('email'),
            otp=self.request.data.get('otp')
        ).first()
        if otp and otp.is_valid(otp) and otp.otp == int(self.request.data.get('otp')):
            user = User.objects.filter(id=otp.user.id).update(is_active=True)
            if user == 1:
                notification = Notification()
                notification.publish('Sigup', 'Account has been verified',
                                     user.id, notification.TYPE_EMAIL, notification.EVENT_SIGNUP)

                return Response({'ok': 'Your account has been activated successfully'})
            return Response({'error': 'Something went wrong !'}, status=500)
        return Response({'error': 'Invalid otp'}, status=400)


class UserLogin(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get or Generate token
        token, created = Token.objects.get_or_create(
            user=serializer.validated_data['user'])
        request = {
            'user': serializer.validated_data['user']
        }

        # If Token was already present, update created time so that its valid for the full duration
        if not created:
            token.created = timezone.now()
            token.save(update_fields=['created'])

        # Store token to redis server
        cache_storage = RemoteTokenStorage()
        cache_storage.set_token(token.key, token.user.id)

        reply_serializer = UserLoginReplySerializer(
            token, context={'request': request})
        return Response(reply_serializer.data)


class UserLoginCustom(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        print('login')
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        print('request', request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        print('user is : ', user)
        token = Token.objects.get(user=user)
        # token = Token.objects.create(user=user)
        print('token', token)

        reply_serializer = UserLoginReplySerializer(
            token, context={'request': request})
        return Response(reply_serializer.data)


class UsersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UsersListSerializer
    permission_classes = ()


class TokenUserView(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        query = User.objects.get(id=pk)
        serializer = UserSerializer(query)
        return Response(serializer.data)


class UsersDetailsView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UsersListSerializer
    permission_classes = ()


class AnalyticUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = AnalyticsUpdateSerializer
    permission_classes = ()


class ForgotPasswordView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UsersListSerializer
    permission_classes = ()

    def get_object(self):
        email = self.kwargs["email"]
        return get_object_or_404(User, email=email)


@api_view(["POST"])
def forgotPasswordotpView(request):
    username = request.data.get('username')

    if username:
        user = get_object_or_404(User, username=username)

    otp_helper(country_code=user.phone_code,
               phone=user.phone, email=user.email)

    return Response({'success': 'otp sent'},
                    status=200)


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = ()

    def update(self, request, *args, **kwargs):
        password = request.data.get("password")
        confirmPassword = request.data.get("confirmPassword")
        token_key = request.data.get("token")
        if password != confirmPassword:
            return Response({'error': 'Password does not match'},
                            status=500)
        token = get_object_or_404(Token, key=token_key)

        user = get_object_or_404(User, id=token.user.id)
        user.set_password(password)
        user.save()
        if user is not None:
            notification = Notification()
            notification.publish(
                'Your password has been changed succesfully', user.phone_code +
                user.phone, user.id, notification.TYPE_MSG, notification.EVENT_FORGOT_PWD
            )
            notification.publish(
                'Reset Password Confirm', '', user.id, notification.TYPE_PUSH, notification.EVENT_FORGOT_PWD
            )
            notification.publish(
                'Reset Password Confirm', user.email, user.id, notification.TYPE_EMAIL, notification.EVENT_FORGOT_PWD
            )
            return Response({'ok': 'Password changed successfully! '},
                            status=200)


@api_view(["POST"])
def verify_otp(request):
    otp = request.data.get("otp")
    phone = request.data.get('phone')
    event = request.data.get('event')
    if otp is None:
        return Response({'error': 'Please provide Otp'},
                        status=500)
    if event == 'forgot_password':
        # user = get_object_or_404(User, username=phone)
        user_otp = get_object_or_404(PhoneNumberOtp, phone=phone, otp=otp)
        print('users', user_otp)
        if user_otp.is_valid():
            return Response({'ok': phone},
                            status=200)

    if event == 'signup':
        PhoneNumberOtp_obj = get_object_or_404(PhoneNumberOtp, phone=phone)
        if PhoneNumberOtp_obj.is_verified:
            return Response({'error': 'Phone number already verified'},
                            status=500)
        if PhoneNumberOtp_obj.is_valid() and PhoneNumberOtp_obj.otp == int(request.data.get('otp')):
            PhoneNumberOtp_obj.is_verified = True
            PhoneNumberOtp_obj.save()
            return Response({'ok': PhoneNumberOtp_obj.phone},
                            status=200)
    return Response({'error': "Invalid otp"}, status=500)


# after using otp  must need usr phone in request data
@api_view(["POST"])
def reset_password(request):
    password = request.data.get("password")
    # confirmPassword = request.data.get("confirmPassword")
    username = request.data.get("username")

    # if password is None or password != confirmPassword :
    #     return Response({'error': 'Password does not match'},
    #                     status=500)

    user = get_object_or_404(User, username=username)
    print('api/v1/reset-password/', user)
    user.set_password(password)
    user.save()
    return Response({'success': "Password Reset Successfully"}, status=200)
    # if user is not None:
    #     notification = Notification()
    #     notification.publish(
    #         'Your password has been changed succesfully', user.phone_code + user.phone, user.id, notification.TYPE_MSG, notification.EVENT_FORGOT_PWD
    #     )
    #     notification.publish(
    #         'Your password has been changed succesfully', 'Your password has been changed succesfully', user.id, notification.TYPE_PUSH, notification.EVENT_FORGOT_PWD
    #     )
    #     notification.publish(
    #         'Your password has been changed succesfully', user.email , user.id, notification.TYPE_EMAIL, notification.EVENT_FORGOT_PWD
    #     )
    #     return Response({'ok': 'Password changed successfully! '},
    #                     status=200)

    # return Response({'error': "Internal server error"}, status=500)


@api_view(["POST"])
def phoneNumberOtpView(request):
    phone = request.data.get('phone')
    email = request.data.get('email')
    country_code = request.data.get('country_code')
    otp_helper(country_code=country_code, phone=phone, email=email)


def otp_helper(country_code=None, phone=None, email=None):
    phone = phone
    email = email
    country_code = country_code
    if email:
        print('email')
        if email is None or len(email) < 10:
            return({'error': 'Please provide valid a Email', 'status': 500})
        PhoneNumberOtp_obj, created = PhoneNumberOtp.objects.get_or_create(
            phone=email, otp=randint(1000, 9999))
        # if not created and PhoneNumberOtp_obj.is_verified:
        #     return({'error': 'Email already registered with another account', 'status': 500})
        # if not PhoneNumberOtp_obj.is_valid():
        #     PhoneNumberOtp_obj.otp = randint(1000, 9999)
        #     PhoneNumberOtp_obj.save()
        # notification = Notification()
        # notification.publish(
        #     PhoneNumberOtp_obj.otp,
        #     email, '0',
        #     notification.TYPE_EMAIL, notification.EVENT_SIGNUP
        # )
        return ({'ok': 'An otp has been sent to verify email!', 'status': 200})
    else:
        if phone:
            print('phone')
            if phone is None or len(phone) < 10:
                return ({'error': 'Please provide valid a Mobile Number', 'status': 500})
            PhoneNumberOtp_obj, created = PhoneNumberOtp.objects.get_or_create(
                phone=phone, otp=randint(1000, 9999))
            if not created and PhoneNumberOtp_obj.is_verified:
                return ({'error': 'Phone number already registered with another account', 'status': 500})
            if not PhoneNumberOtp_obj.is_valid():
                PhoneNumberOtp_obj.otp = randint(1000, 9999)
                PhoneNumberOtp_obj.save()
            notification = Notification()
            notification.publish(
                PhoneNumberOtp_obj.otp,
                country_code + phone, '0',
                notification.TYPE_MSG, notification.EVENT_SIGNUP
            )
            return({'ok': 'An otp has been sent to verify mobile no.!', 'status': 200})


class UserLastSeenLogView(viewsets.ModelViewSet):
    queryset = UserLastSeenLog.objects.all()
    serializer_class = UserLastSeenLogSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def retrieve(self, request, pk=None):
        # here we are yous pk as user_id
        obj = get_object_or_404(UserLastSeenLog, user=pk)
        serializer = UserLastSeenLogSerializer(obj)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        obj = UserLastSeenLog.objects.get(user=request.user)
        obj.status = request.data.get('status')
        obj.save()
        return Response({'success': "ok"}, status=201)


@api_view(['GET'])
def listuser(request, userId):
    res = userId.strip('][').split(',')
    data = []
    for i in res:
        if i != ',':
            try:
                user = User.objects.get(id=int(i))
                profile_serializer = UsersListSerializer(user)
                user_profile = {
                    f'fname{i}': profile_serializer.data['first_name'], f'picture{i}': profile_serializer.data['picture']}
                data.append(user_profile)
            except:
                pass
    return Response(data)


class listuserpost(APIView):
    """
    List all snippets, or create a new snippet.
    """

    def post(self, request, format=None):
        userId = request.data['id']
        res = userId.strip('][').split(',')
        data = []
        for i in res:
            if i != ',':
                try:
                    user = User.objects.get(id=int(i))
                    profile_serializer = UsersListSerializer(user)
                    user_profile = {
                        f'fname{i}': profile_serializer.data['first_name'], f'picture{i}': profile_serializer.data['picture']}
                    data.append(profile_serializer.data)
                except:
                    pass
        return Response(data)


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ForgetPasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteVerifyotp(generics.UpdateAPIView):

    def get_object(self, phone):
        try:
            return PhoneNumberOtp.objects.get(phone=phone)
        except:
            return '404'

    def delete(self, request, phone, format=None):
        otp = self.get_object(phone)
        otp.delete()
        return Response({'Otp Deleted'}, status=200)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class Usersearch(viewsets.ModelViewSet):

    serializer_class = UsersListSerializer
    queryset = User.objects.all()
    filter_backends = [SearchFilter, ]
    search_fields = ['first_name', 'last_name', 'id', 'username']
