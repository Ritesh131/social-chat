# Model
from django.db import models
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from authentication.models import User
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
import os

PENDING = 0
ACCEPTED = 1
INVITED = 2
RECEIVED = 3
REJECTED = 4

STATUS_CHOICES = (
    (PENDING, 'PENDING'),
    (ACCEPTED, 'ACCEPTED'),
    (INVITED, 'INVITED'),
    (RECEIVED, 'RECEIVED'),
    (REJECTED, 'REJECTED'),
)

PHONE = 0
FACEBOOK = 1
TWITTER = 2
GMAIL = 3

SOURCE_CHOICES = (
    (PHONE, 'PHONE'),
    (FACEBOOK, 'FACEBOOK'),
    (TWITTER, 'TWITTER'),
    (GMAIL, 'GMAIL')
)


def post_directory_path(instance, filename):
    upload_path = f'post_{instance.id}/{filename}'
    return upload_path


def group_directory_path(instance, filename):
    upload_path = f'group_{instance.id}/{filename}'
    return upload_path


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    profileId = models.IntegerField(
        default=None, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    mobile_no = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    unique_id = models.CharField(max_length=100, null=True, blank=True)
    is_registered = models.BooleanField(default=False)
    is_connected = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=PENDING)
    is_invited = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=PENDING)
    registered_id = models.IntegerField(default=None, null=True, blank=True)
    source = models.PositiveSmallIntegerField(
        choices=SOURCE_CHOICES, default=PHONE)
    from_request = models.IntegerField(
        default=None, blank=True)
    to_request = models.IntegerField(
        default=None, blank=True)

    def __str__(self):
        return self.name


class UserPost(models.Model):
    # upload_storage = FileSystemStorage(location=settings.PICTURE_MEDIA_ROOT, base_url=settings.PICTURE_MEDIA_URL)
    post_content = models.CharField(
        max_length=500, null=True, blank=True, default="")
    post_image = models.ImageField(
        upload_to=post_directory_path, null=True, blank=True, default=None)
    post_user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    created_on = models.DateField(auto_now=True)
    post_user_name = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.post_user_name


class Comments(models.Model):
    post_id = models.ForeignKey(
        UserPost, on_delete=models.CASCADE, null=True, blank=True)
    comment_userid = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    comment_username = models.CharField(max_length=100, default="")
    comment_title = models.CharField(max_length=500, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment_title


class Group(models.Model):
    SPORT = 0
    EDUCATION = 1
    ORGANIZATION = 2
    ENTERTAINMENT = 3
    DEFAULT = 4

    category = (
        (DEFAULT, 'DEFAULT'),
        (SPORT, 'SPORT'),
        (EDUCATION, 'EDUCATION'),
        (ORGANIZATION, 'ORGANIZATION'),
        (ENTERTAINMENT, 'ENTERTAINMENT')
    )
    group_name = models.CharField(max_length=200, default="")
    group_category = models.CharField(choices=category, max_length=100)
    group_profile = models.ImageField(
        upload_to=group_directory_path, null=True, blank=True, default=None)
    group_cover = models.ImageField(
        upload_to=group_directory_path, null=True, blank=True, default=None)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    admin_name = models.CharField(max_length=60, default="")

    def __str__(self):
        return self.group_name


class Page(models.Model):
    SPORT = 0
    EDUCATION = 1
    ORGANIZATION = 2
    ENTERTAINMENT = 3
    DEFAULT = 4

    category = (
        (DEFAULT, 'DEFAULT'),
        (SPORT, 'SPORT'),
        (EDUCATION, 'EDUCATION'),
        (ORGANIZATION, 'ORGANIZATION'),
        (ENTERTAINMENT, 'ENTERTAINMENT')
    )
    page_name = models.CharField(max_length=200, default="")
    page_category = models.CharField(choices=category, max_length=100)
    page_profile = models.ImageField(
        upload_to=group_directory_path, null=True, blank=True, default=None)
    page_cover = models.ImageField(
        upload_to=group_directory_path, null=True, blank=True, default=None)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    admin_name = models.CharField(max_length=60, default="")

    def __str__(self):
        return self.page_name
