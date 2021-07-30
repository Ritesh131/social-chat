from django.db import models
from .helpers import *
from authentication.models import User
from art_group.models import *

# Create your models here.

def notification_signal(created_by, message):
    try:
        UserNotification.objects.create(notice_user=created_by, message=message)
        return True
    except Exception as e:
        print(e)
        return False


class ArtImages(models.Model):
    craft = models.FileField(upload_to='directory_path')


class ArtComment(models.Model):
    comment = models.CharField(
        max_length=500, null=True, blank=True, default='')
    comment_user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE, default=1)


Art_Category = (
    ('sport', 'SPORT'),
    ('education', 'EDUCATION'),
    ('organization', 'ORGANIZATION'),
    ('entertainment', 'ENTERTAINMENT'),
    ('animation', 'ANIMATION')
)


class UserArt(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, blank=True, null=True, default='')
    category = models.CharField(
        max_length=200, blank=True, null=True, default='')
    art_images = models.ManyToManyField(ArtImages, blank=True)
    media_type = models.CharField(max_length=100, default='image')
    thumbnail = models.FileField(upload_to='directory_path', blank=True, null=True)
    tag = models.CharField(max_length=200, blank=True, null=True, default='')
    description = models.CharField(
        max_length=200, blank=True, null=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    likes = models.ManyToManyField(
        User, blank=True, related_name="users_like")
    comment = models.ManyToManyField(
        ArtComment, blank=True, related_name="users_comment")
    upload_date = models.DateField(auto_now=True)
    upload_time = models.TimeField(auto_now=True)

    # def save(self, *args, **kwargs):
    #     message = f'you have successfully created Art with title - "{self.title}"'
    #     notification_signal(self.created_by, message)
    #     return super().save(*args, **kwargs)


class UserFollowers(models.Model):
    user_id = models.ForeignKey(
        User, related_name="following", on_delete=models.CASCADE)
    following_user_id = models.ForeignKey(
        User, related_name="followers", on_delete=models.CASCADE)
    created = models.DateField(auto_now=True)
    created_time = models.TimeField(auto_now=True)


class UserNotification(models.Model):
    notice_user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=400, default='')
    created_date = models.DateField(auto_now=True)
