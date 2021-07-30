from django.db import models
from authentication.models import User

# Create your models here.
class PaymentRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.CharField(max_length=5000, default='')  
    payment_message = models.CharField(max_length=300, null=True, blank=True)
    account_id = models.CharField(max_length=300, null=True, blank=True)
    charge_id = models.CharField(max_length=300, null=True, blank=True)


class StripeUserAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_id = models.CharField(max_length=500, default='')
    created_date = models.DateField(auto_now=True)


class PaymentHistory(models.Model):
    payment_from = models.ForeignKey(User, default=None, related_name='payment_from', on_delete=models.CASCADE)
    payment_to = models.ForeignKey(User, default=None, related_name='payment_to', on_delete=models.CASCADE)
    amount = models.CharField(default='', max_length=2000)
    transaction_id = models.CharField(max_length=500, default='')
    created_date = models.DateField(auto_now=True)


class PaypalKey(models.Model):
    payer_id = models.CharField(max_length=200, default='')
    amount = models.CharField(max_length=2000, default='')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_date = models.DateField(auto_now=True)