from django.urls import path

from authentication.views import (
    UserRegister, UserLogin, Countries, UserOtpViewSet,
    UsersView, UsersDetailsView, AnalyticUpdateView,
    forgotPasswordotpView, verify_otp, UserLastSeenLogView,
    reset_password, phoneNumberOtpView, UserUpdate, ChangePasswordView, listuser, TokenUserView,
    listuserpost, ChangePasswordView, ForgetPasswordView, DeleteVerifyotp, UserViewSet, Usersearch, UserLoginCustom
)
from rest_framework.routers import DefaultRouter
from django.conf.urls import url, include
from rest_framework.authtoken import views
from .api_authview import *

router = DefaultRouter()

router.register(r'otp_verification', UserOtpViewSet, 'user-otp')
router.register(r'user-last-seen', UserLastSeenLogView, 'last-seen')
router.register(r'shofor', UserViewSet)
router.register(r'user/search', Usersearch)


urlpatterns = [
    url('api/', include(router.urls)),
    path('api/v1/login', UserLoginCustom.as_view(), name='api-tokn-auths'),
    path('api/v1/countries', Countries.as_view(), name='countries-list'),
    path('api/v1/register', UserRegister.as_view()),
    path('api/v1/user-pic/<int:pk>', UserUpdate.as_view()),
    #     path('api/v1/login', UserLogin.as_view()),
    path('api/v1/users', UsersView.as_view(), name="users-list"),
    path('api/v1/token/user/<pk>', TokenUserView.as_view()),
    path('api/v1/users/list/post', listuserpost.as_view()),
    path(r'api/v1/users/list/<userId>', listuser),
    path('api/v1/users/<int:pk>/<str:slug>',
         UsersDetailsView.as_view(), name="users-details"),
    path('api/v1/users/<int:pk>',
         UsersDetailsView.as_view(), name="users-details"),
    path('api/v1/users/<int:pk>/analytic',
         AnalyticUpdateView.as_view(), name='user-analytic-update'),
    path('api/v1/forgot-password/', forgotPasswordotpView, name='forgot-password'),
    path('api/v1/set-password/', ForgetPasswordView, name='forgot-passkey'),
    path('api/v1/change-password/',
         ChangePasswordView.as_view(), name='change-password'),
    path('api/v1/verify-otp/', verify_otp, name='verify-otp'),
    path('api/v1/reset-password/', reset_password, name='reset-password'),
    path('api/v1/phone-otp/', phoneNumberOtpView, name='phone-otp'),
    path('api/v1/password_reset/',
         include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/v1/otp/verify/<phone>',
         DeleteVerifyotp.as_view(), name='phone-otp-delete'),

     path('api/v1/otp', OTPView.as_view()),
     path('api/v1/reset/password', PasswordResetView.as_view()),
]
