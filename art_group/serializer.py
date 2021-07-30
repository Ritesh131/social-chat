from rest_framework import serializers
from authentication.serializers import UserSerializer
from art_group.models import *
from art_app.models import *
from art_app.serializers import *


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class GroupPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPost
        fields = '__all__'


class GroupPostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = '__all__'


class GroupPostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = '__all__'


class GroupPostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = '__all__'


class GroupDetailSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()
    member = UserSerializer(many=True)

    class Meta:
        model = Group
        fields = '__all__'


class GroupInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupInvite
        fields = '__all__'


class GroupInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupInvite
        fields = '__all__'


class GroupInviteDetailSerializer(serializers.ModelSerializer):
    group = GroupDetailSerializer()

    class Meta:
        model = GroupInvite
        fields = '__all__'


class GroupPostDetailSerializer(serializers.ModelSerializer):
    comment = CommentUserSerializer(many=True)
    art_images = ArtImagesSerializer(many=True, read_only=True)
    created_by = UserSerializer()
    group = GroupDetailSerializer()

    class Meta:
        model = UserArt
        fields = "__all__"
