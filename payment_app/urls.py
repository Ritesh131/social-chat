from django.urls import path
from .views import *

urlpatterns = [
    path('stripe/charge', ChargeView.as_view()),
    path('stripe/account/create', StripeAccountCreate.as_view()),
    path('total/debit', PaymentDebitHistoryView.as_view()),
    path('total/credit', PaymentCreditHistoryView.as_view()),
    path('paypal', PaypalPaymentView.as_view()),
    path('paypal/payout', UserPayout.as_view()),
]