from django.db.models import fields
from rest_framework import serializers
from .models import *
from authentication.serializers import UserSerializer

class PaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRecord
        fields = "__all__"


class PaymentDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = PaymentRecord
        fields = "__all__"


class StripeAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = StripeUserAccount
        fields = '__all__'


class PaymentHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentHistory
        fields = '__all__'


class PaymentHistoryDetailSerializer(serializers.ModelSerializer):
    payment_from = UserSerializer()
    payment_to = UserSerializer()

    class Meta:
        model = PaymentHistory
        fields = '__all__'