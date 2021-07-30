from django.db.models import fields
from rest_framework import serializers
from authentication.serializers import UserSerializer
from .models import *


class ArtImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtImages
        fields = "__all__"


class UserArtSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserArt
        fields = "__all__"


class UserArtDetailSerializer(serializers.ModelSerializer):
    art_images = ArtImagesSerializer(many=True, read_only=True)

    class Meta:
        model = UserArt
        fields = "__all__"


class FollowersSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollowers
        fields = "__all__"


class FollowerDetailSerializer(serializers.ModelSerializer):
    following_user_id = UserSerializer()

    class Meta:
        model = UserFollowers
        fields = "__all__"


class FollowerFollowingDetailSerializer(serializers.ModelSerializer):
    following_user_id = UserSerializer()
    user_id = UserSerializer()

    class Meta:
        model = UserFollowers
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtComment
        fields = "__all__"


class CommentUserSerializer(serializers.ModelSerializer):
    comment_user = UserSerializer()

    class Meta:
        model = ArtComment
        fields = "__all__"


class UserArtCommentSerializer(serializers.ModelSerializer):
    comment = CommentUserSerializer(many=True)
    art_images = ArtImagesSerializer(many=True, read_only=True)
    created_by = UserSerializer()

    class Meta:
        model = UserArt
        fields = "__all__"


class UserNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserNotification
        fields = '__all__'