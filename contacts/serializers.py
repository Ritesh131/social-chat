#
from rest_framework import serializers
from django.db.models import Q

from contacts.models import Contact, UserPost, Comments, Group, Page
from authentication.models import User, UserLastSeenLog

from django.db import connections


class ContactsSerializer(serializers.ModelSerializer):
    registered_id = serializers.IntegerField(read_only=True)
    profileId = serializers.IntegerField(read_only=True)
    connected_contacts_count = serializers.SerializerMethodField()
    connected_contacts_deal_count = serializers.SerializerMethodField()
    last_seen = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        exclude = ('user',)

    def create(self, validated_data):
        if Contact.objects.filter(mobile_no=validated_data['mobile_no'], user=validated_data['user']).exists():
            return Contact.objects.filter(mobile_no=validated_data['mobile_no'], user=validated_data['user']).first()

        # Mark is_registered flag true if user already exist in users.
        if User.objects.filter(Q(phone=validated_data['mobile_no'].replace(validated_data['user'].phone_code, ''))).exists():
            user = User.objects.filter(Q(phone=validated_data['mobile_no'].replace(
                validated_data['user'].phone_code, ''))).first()
            validated_data['is_registered'] = True
            validated_data['registered_id'] = user.id
        return Contact.objects.create(**validated_data)

    def get_connected_contacts_count(self, obj):
        if obj.is_registered and obj.is_connected == 1:
            return {
                'count': Contact.objects.filter(is_connected=1, user=obj.user).count(),
                'date_joined': User.objects.get(id=obj.registered_id).date_joined
            }
        return

    def get_connected_contacts_deal_count(self, obj):
        if obj.registered_id and obj.is_connected == 1:
            cursor = connections['deal_db'].cursor()
            return cursor.execute("SELECT count(*) FROM deal WHERE user_id = {}".format(obj.registered_id))
        return

    def get_last_seen(self, obj):
        if obj.is_registered:
            temp = UserLastSeenLog.objects.filter(
                user=obj.registered_id).first()
            if temp:
                return {
                    "status": temp.status,
                    "time": temp.updated_at
                }
        return

    registered_id_profile = serializers.SerializerMethodField(
        'get_profile_pic')
    profileId_profile = serializers.SerializerMethodField('get_profile_pic2')

    def get_profile_pic(self, obj):
        print('req.user', self.context['request'].user)
        if obj.is_registered:
            user = User.objects.filter(id=obj.registered_id).first()
            if user and user.picture:
                return self.context['request'].build_absolute_uri(user.picture.url)
        return

    def get_profile_pic2(self, obj):
        print('req.user', self.context['request'].user)
        if obj.is_registered:
            user = User.objects.filter(id=obj.profileId).first()
            if user and user.picture:
                return self.context['request'].build_absolute_uri(user.picture.url)
        return

    registered_id_name = serializers.SerializerMethodField('get_profile_name1')
    profileId_name = serializers.SerializerMethodField('get_profile_name2')

    def get_profile_name1(self, obj):
        if obj.is_registered:
            user = User.objects.filter(id=obj.registered_id).first()
            return user.first_name + " " + user.last_name
        return

    def get_profile_name2(self, obj):
        print('req.user', self.context['request'].user)
        if obj.is_registered:
            user = User.objects.filter(id=obj.profileId).first()
            return user.first_name + " " + user.last_name
        return

    registered_id_dob = serializers.SerializerMethodField('get_profile_dob1')
    profileId_dob = serializers.SerializerMethodField('get_profile_dob2')

    def get_profile_dob1(self, obj):
        if obj.is_registered:
            user = User.objects.filter(id=obj.registered_id).first()
            return user.date_of_birth
        return

    def get_profile_dob2(self, obj):
        print('req.user', self.context['request'].user)
        if obj.is_registered:
            user = User.objects.filter(id=obj.profileId).first()
            return user.date_of_birth
        return


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPost
        fields = '__all__'


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class Commentserializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'


class Groupserializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class Pageserializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'
