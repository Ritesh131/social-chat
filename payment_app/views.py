from django.db.models import query
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from icecream import ic
import stripe
from users import settings
from .serializer import *
from rest_framework.permissions import IsAuthenticated
import paypalrestsdk
import logging

# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY

# Paypal configure
paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": settings.PAYPAL_CLIENT_ID,
  "client_secret": settings.PAYPAL_SECRET_ID
  })


class ChargeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = PaymentRecord.objects.filter(user=request.user)
        serializer = PaymentDetailSerializer(query, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        exp_month = request.data['expiry'][0:2]
        exp_year = request.data['expiry'][3:5]
        amount_sent = int(request.data['amount'])*100
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
            payment_data['payment_to'] = request.data['payment_to']
            payment_data['amount'] = request.data['amount']
            payment_data['transaction_id'] = account.id

            serializer = PaymentHistorySerializer(data=payment_data)
            if serializer.is_valid():
                serializer.save()
                print(serializer.data)
            try:
                res_payout = payout_artist(
                    request.data['payment_to'], request.data['amount'])
                print('res_payout', res_payout)
            except Exception as e:
                ic(e)
            return Response({'stripe_res': charge_create})
        return Response({'message': account}, status=status.HTTP_400_BAD_REQUEST)


class StripeAccountCreate(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = StripeUserAccount.objects.filter(user=request.user)
        if len(query) >= 1:
            return Response({'message': 'Your account is allready register with Stripe', 'account': True}, status=400)
        return Response({'account': False}, status=200)

    def post(self, request, format=None):
        # request.user.email or request.user.username
        email = 'bajpairitesh878@gmail.com'
        print(f'account {email}')
        account_response = stripe.Account.create(
            type="express",
            country="US",
            email=email,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
        )
        print(f'account {account_response}')
        if account_response.id:
            data = {
                'user': request.user.pk,
                'account_id': account_response.id
            }
            serializer = StripeAccountSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                print('serializer', serializer.data)
                # Create stripe account link
                accountlink = stripe.AccountLink.create(
                    account=account_response.id,
                    refresh_url="https://appandgo.keycorp.in/api/v1/trip/payment/stripe/driver/account/success",
                    return_url="https://appandgo.keycorp.in/api/v1/trip/payment/stripe/driver/account/success",
                    type="account_onboarding",
                )
                return Response({'message': accountlink, 'status': status.HTTP_200_OK})
            return Response({'message': serializer.errors, 'status': status.HTTP_400_BAD_REQUEST})
        return Response({'message': 'There are some problem to create your account', 'status': status.HTTP_400_BAD_REQUEST})


def payout_artist(user_id, amount):
    user_token = StripeUserAccount.objects.filter(
        user=user_id).last().account_id
    if user_token:
        payout_response = stripe.Payout.create(
            amount=amount,
            currency="usd",
            stripe_account=user_token,
            method='standard',
        )
        print(f'payout_response, {payout_response}')
        return True
    return False


class PaymentDebitHistoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = PaymentHistory.objects.filter(
            payment_from=request.user).order_by('-id')
        serializer = PaymentHistoryDetailSerializer(query, many=True)
        return Response(serializer.data)


class PaymentCreditHistoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = PaymentHistory.objects.filter(
            payment_to=request.user).order_by('-id')
        serializer = PaymentHistoryDetailSerializer(query, many=True)
        return Response(serializer.data)


class PaypalPaymentView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request): 
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
                },
            "redirect_urls": {
                "return_url": request.data['return_url'],
                "cancel_url": request.data['cancel_url']
                },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "item",
                        "sku": "item",
                        "price": request.data['amount'],
                        "currency": "USD",
                        "quantity": 1
                        }]
                    },
                "amount": {
                    "total": request.data['amount'],
                    "currency": "USD"},
                "description": "This is the payment transaction description."}]})

        print('payment.error', payment)

        if payment.create():
            print(payment)
            # Extract redirect url
            for link in payment.links:
                if link.method == "REDIRECT":
                    # save payer
                    try:
                        res_paypal = PaypalKey.objects.create(user=request.user, amount=request.data['amount'], 
                                                            payer_id=payment['id'])
                        print(res_paypal)
                    except:
                        print('error')

                    try:
                        payload = {
                            'payment_from': request.user.pk,
                            'payment_to': request.data['payment_to'],
                            'amount': request.data['amount'],
                            'transaction_id': payment['id']
                        }
                        serializer = PaymentHistorySerializer(data=payload)
                        if serializer.is_valid():
                            serializer.save()
                            print(serializer.data)
                        print(serializer.errors)
                    except:
                        pass
                    
                # Capture redirect url
                    redirect_url = (link.href)
                    return Response({'payment_url':redirect_url})
            return Response('payments')
        else:
            print("Error while creating payment:")
            print(payment.error)
            return Response({'message':'Payment not done', status:400})


class UserPayout(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        payout = paypalrestsdk.Payout({
            "sender_batch_header": {
                "sender_batch_id": "batch_1",
                "email_subject": "You have a payment"
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": 0.99,
                        "currency": "USD"
                    },
                    "receiver": request.data['email'],
                    "note": "Thank you.",
                    "sender_item_id": "item_1"
                }
            ]
        })

        if payout.create(sync_mode=False):
            print("payout[%s] created successfully" %
                (payout.batch_header.payout_batch_id))
            return Response('success')
        else:
            print(payout.error)
            return Response('error')