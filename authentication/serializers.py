from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import serializers, exceptions
from rest_framework.authtoken.models import Token

from authentication.models import *
from django.db import models
from contacts.models import Contact
from django.db import connections


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'


class UserOtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOtp
        fields = ('__all__')


class UserSerializer(serializers.ModelSerializer):
    # userotp_set = UserOtpSerializer(required=True, many=True)
    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions')


class UserRegisterSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender', 'date_of_birth',
                  'phone', 'phone_code', 'password', 'username', 'token']
        extra_kwargs = {'password': {'write_only': True,
                                     'style': {'input_type': 'password'}}}

    def validate_password(self, value):
        return make_password(value)

    def get_token(self, obj):
        token = Token.objects.create(user=obj)
        return token.key


class UserLoginSerializer(serializers.Serializer):
    phone_code = serializers.CharField(max_length=3)
    username = serializers.CharField(max_length=35)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        user = authenticate(
            username=data['username'], password=data['password'])
        if not user:
            raise exceptions.AuthenticationFailed()
        elif not user.is_active:
            raise exceptions.PermissionDenied()

        # Update last login information whenever token is requested
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        data['user'] = user
        return data


class UserLoginReplySerializer(serializers.ModelSerializer):
    user = UserSerializer()
    # connected_contacts_count = serializers.SerializerMethodField()
    # deal_count = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = ('key', 'user')

    # def get_connected_contacts_count(self, obj):
    #     return Contact.objects.filter(is_connected=1, user=obj.user.id).count()

    # def get_deal_count(self, obj):
    #     cursor = connections['deal_db'].cursor()
    #     return cursor.execute("SELECT * FROM deal WHERE user_id = {}".format(obj.user.id))


class UsersListSerializer(serializers.ModelSerializer):
    connection_status = serializers.CharField(
        source='get_connection_status_display')

    class Meta:
        model = User
        exclude = ('password',)


class UserLastSeenLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLastSeenLog
        fields = '__all__'


class AnalyticsUpdateSerializer(serializers.ModelSerializer):
    CONNECTION_STATUS = (
        ('S', 'Send'),
        ('R', 'Received')
    )
    DEAL_STATUS = (
        ('R', 'Requested'),
        ('A', 'Accepted'),
        ('P', 'Proposed')
    )
    login_status = serializers.ChoiceField(
        required=False, choices=User.CONNECTION_STATUS, source='connection_status')
    connection_status = serializers.ChoiceField(
        required=False, choices=CONNECTION_STATUS)
    deal_status = serializers.ChoiceField(required=False, choices=DEAL_STATUS)

    class Meta:
        model = User
        fields = ('login_status', 'connection_status', 'deal_status')

    def update(self, instance, validated_data):

        if validated_data.get('connection_status', None):
            if validated_data.get('connection_status') == 'S':
                instance.connection_sent = instance.connection_sent + 1
            elif validated_data.get('connection_status') == 'R':
                instance.connection_received = instance.connection_received + 1
        if validated_data.get('deal_status', None):
            if validated_data.get('deal_status') == 'R':
                instance.deal_requested = instance.deal_requested + 1
            elif validated_data.get('deal_status') == 'A':
                instance.deal_accepted = instance.deal_accepted + 1
            elif validated_data.get('deal_status') == 'P':
                instance.deal_proposed = instance.deal_proposed + 1
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ForgetPasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    username = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields = '__all__'
