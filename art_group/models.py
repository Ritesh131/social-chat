from django.db import models
from authentication.models import User
from django.template.defaultfilters import slugify


# Create your models here.


class Group(models.Model):
    GROUP_CATEGORY = (
        ('sport', 'SPORT'),
        ('education', 'EDUCATION'),
        ('organization', 'ORGANIZATION'),
        ('entertainment', 'ENTERTAINMENT')
    )
    member = models.ManyToManyField(User, related_name='group_member', blank=True)
    name = models.CharField(max_length=150)
    slug = models.SlugField(null=True, blank=True)
    profile_image = models.FileField(null=True, blank=True, upload_to='group')
    cover_image = models.FileField(null=True, blank=True, upload_to='group')
    categoy = models.CharField(
        choices=GROUP_CATEGORY, max_length=100, default='sport')
    about = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='group_user')
    created_on = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

            return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)


class PostComment(models.Model):
    comment = models.CharField(
        max_length=500, null=True, blank=True, default='')
    comment_user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now=True)


class PostLike(models.Model):
    likes = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)


class GroupPost(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_user")
    title = models.CharField(max_length=250, default='')
    thumbnil = models.FileField(null=True, blank=True)
    second_img = models.FileField(null=True, blank=True)
    third_img = models.FileField(null=True, blank=True)
    description = models.CharField(
        max_length=200, blank=True, null=True, default='')
    likes = models.ManyToManyField(PostLike, blank=True)
    comment = models.ManyToManyField(
        PostComment, blank=True, related_name="users_comment")
    upload_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class GroupInvite(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_invited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
