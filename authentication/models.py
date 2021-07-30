import os
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as __
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from random import randint
from datetime import datetime, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
import pytz
from django.conf import settings
from notification.notification import Notification
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.utils.text import slugify

utc = pytz.UTC


class Country(models.Model):

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=3)
    phone_code = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        verbose_name = __('Country')
        verbose_name_plural = __('Countries')

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, phone, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        if not phone:
            raise ValueError('Users must have an phone number')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, username, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email, username, first_name, last_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.username = username
        user.is_active = True
        user.save(using=self._db)
        return user


def user_directory_path(instance, filename):
    upload_path = 'user_{0}/{1}'.format(instance.id, filename)
    return upload_path


class User(AbstractBaseUser, PermissionsMixin):

    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_OTHER = 'O'

    GENDER_OPTIONS = (
        (GENDER_MALE, __('Male')),
        (GENDER_FEMALE, __('Female')),
        (GENDER_OTHER, __('Other'))
    )

    CONNECTION_ONLINE = 'O'
    CONNECTION_OFFLINE = 'F'

    CONNECTION_STATUS = (
        (CONNECTION_ONLINE, __('Online')),
        (CONNECTION_OFFLINE, __('Offline'))
    )

    PROFILE_PRIVACY = (
        ('PUBLIC', 'PUBLIC'),
        ('PRIVATE', 'PRIVATE'),
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    upload_storage = FileSystemStorage(
        location=settings.PICTURE_MEDIA_ROOT, base_url=settings.PICTURE_MEDIA_URL)
    username = models.CharField(
        max_length=35, unique=True, null=True, blank=True)
    email = models.EmailField(
        verbose_name='email address', null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    slug = models.SlugField(default='', editable=False, max_length=500)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    phone_code = models.CharField(max_length=3, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(
        max_length=1, choices=GENDER_OPTIONS, null=True, blank=True, default='')
    # address information
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    location = models.TextField(default='', null=True, blank=True)
    connection_status = models.CharField(
        max_length=1, choices=CONNECTION_STATUS, default=CONNECTION_OFFLINE)
    connection_sent = models.IntegerField(default=0)
    connection_received = models.IntegerField(default=0)
    deal_requested = models.IntegerField(default=0)
    deal_accepted = models.IntegerField(default=0)
    deal_proposed = models.IntegerField(default=0)
    picture = models.ImageField(upload_to=user_directory_path,
                                storage=upload_storage, null=True, blank=True, default=None)
    cover_picture = models.ImageField(
        upload_to=user_directory_path, storage=upload_storage, null=True, blank=True, default=None)
    pin_enabled = models.BooleanField(default=False)
    post_code = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=100, default="", null=True, blank=True)
    house = models.CharField(max_length=100, default="")
    date_of_birth = models.CharField(max_length=50, default="")
    profile_privacy = models.CharField(
        max_length=20, choices=PROFILE_PRIVACY, default='PUBLIC')
    facebook = models.CharField(max_length=200, null=True, blank=True)
    linkedin = models.CharField(max_length=200, null=True, blank=True)
    twitter = models.CharField(max_length=200, null=True, blank=True)
    instagram = models.CharField(max_length=200, null=True, blank=True)

    objects = UserManager()

    class Meta:
        db_table = 'auth_user'

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.email

    @property
    def picture_url(self):
        return os.path.join(settings.PICTURE_MEDIA_URL, self.picture.name)

    def save(self, *args, **kwargs):
        value = self.first_name + ' ' + self.last_name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)


class UserOtp(models.Model):
    otp = models.IntegerField(default=0)
    user = models.OneToOneField(
        User, related_name='user_otp', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        return self.updated_at + timedelta(seconds=600) > utc.localize(datetime.now())


class PhoneNumberOtp(models.Model):
    otp = models.IntegerField(default=0)
    phone = models.CharField(max_length=30)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        return self.updated_at + timedelta(seconds=600) > utc.localize(datetime.now())


OFFLINE = 0
ONLINE = 1

STATUS_CHOICES = (
    (ONLINE, 'ONLINE'),
    (OFFLINE, 'OFFLINE')
)


class UserLastSeenLog(models.Model):
    user = models.OneToOneField(
        User, related_name='last_seen', on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)

# use for notication
# # @receiver(post_save, sender=User)
# def generate_otp(sender, instance, **kwargs):
#     otp, is_newly_created = UserOtp.objects.get_or_create(user=instance)
#     if not is_newly_created and not otp.is_valid(otp):
#         otp.otp = randint(1000, 9999)
#         otp.save()
#     notification = Notification()
#     notification.publish('OTP_SMS', otp.otp, instance.id, notification.TYPE_MSG, notification.EVENT_SIGNUP)
#     return


def generate_otp_for_reset(user):
    otp, is_newly_created = UserOtp.objects.get_or_create(
        user=user, otp=randint(1000, 9999))
    if not is_newly_created and not otp.is_valid():
        otp.otp = randint(1000, 9999)
        otp.save()
    return otp


class Otp(models.Model):
    OTP_VERIFY = (
        ('true', 'True'),
        ('false', 'False'),
    )
    OTP_TYPE = (
        ('register', 'register'),
        ('forgot', 'forgot'),
    )

    otp = models.IntegerField(default=0)
    type = models.CharField(max_length=20, choices=OTP_TYPE, default='forgot', null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True)
    verify = models.CharField(choices=OTP_VERIFY, default='false', max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
