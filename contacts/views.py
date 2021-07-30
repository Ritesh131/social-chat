# views
import django_filters
import rest_framework.filters
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
import requests

from contacts.serializers import (
    ContactsSerializer, PostSerializer, FriendSerializer, Commentserializer,
    Groupserializer, Pageserializer
)
from authentication.serializers import UsersListSerializer
from authentication.models import User
from contacts.models import Contact, UserPost, Comments, Group, Page
from notification.notification import Notification


class Contacts(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactsSerializer
    # permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10
    filter_fields = ('mobile_no', 'is_invited',
                     'is_connected', 'is_registered', 'name')

    def get_queryset(self):
        queryset = Contact.objects.filter(user=self.request.user, is_registered=False) \
            | Contact.objects.filter(user=self.request.user, is_connected=0)
        return queryset.order_by('-is_registered').distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=201)


class ContactDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Contact.objects.filter(user=self.request.user)
        return queryset

    def partial_update(self, request, *args, **kwargs):
        response_with_updated_instance = super(
            ContactDetail, self).partial_update(request, *args, **kwargs)
        print("partial")
        notification = Notification()
        # sent connection request
        if request.data.get('is_connected') == 2:
            if self.get_object().mobile_no is not None:
                notification.publish(
                    request.user.first_name + request.user.last_name +
                    ' has invited you to register on Social Exchange app : <<tiny url>>',
                    request.user.phone_code +
                    self.get_object().mobile_no, self.get_object().registered_id, notification.TYPE_MSG,
                    notification.EVENT_CONTACT_INVITE
                )

            if self.get_object().email is not None:
                notification.publish(
                    request.user.first_name + request.user.last_name +
                    'has invited you to register on Social Exchange app : <<tiny url>>',
                    self.get_object().email, self.get_object().registered_id, notification.TYPE_EMAIL,
                    notification.EVENT_CONTACT_INVITE
                )
            contacts = Contact.objects.filter(
                user_id=self.get_object().registered_id, registered_id=request.user.id)
            if contacts:
                contacts[0].is_connected = 3
                contacts[0].save()
            if not contacts:
                old_contact = Contact.objects.filter(
                    user_id=self.get_object().registered_id, registered_id=request.user.id
                ).first()
                if old_contact is not None:
                    old_contact.is_connected = 3
                    old_contact.save()
                else:
                    Contact.objects.create(
                        user_id=self.get_object().registered_id, registered_id=request.user.id,
                        name=request.user.first_name, mobile_no=request.user.phone,
                        email=request.user.email, is_registered=True,
                        is_connected=3
                    )

        # if accepted update both parth connection
        if request.data.get('is_connected') == 1:
            print("Creating connection")
            obj = Contact.objects.filter(user_id=self.get_object(
            ).registered_id, registered_id=request.user.id).first()
            if obj:
                obj.is_connected = 1
                obj.save()
        # notification sent on mobile no. invite
        if request.data.get('is_invited') == 2:
            notification.publish('', self.get_object().email, self.get_object(
            ).registered_id, notification.TYPE_EMAIL, notification.EVENT_CONTACT_INVITE)

        return response_with_updated_instance


class MyConnectionList(generics.ListAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactsSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10
    filter_fields = ('mobile_no', 'is_connected', 'name')

    def get_queryset(self):
        queryset = Contact.objects.filter(user=self.request.user, is_connected=3) \
            | Contact.objects.filter(user=self.request.user, is_connected=1)
        return queryset.order_by('-is_connected')


class Postfilter(generics.ListAPIView):
    queryset = UserPost.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post_user', 'post_content']


class PostViewSet(viewsets.ModelViewSet):
    queryset = UserPost.objects.all()
    serializer_class = PostSerializer


class FriendsViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = FriendSerializer


class FriendslistViewSet(generics.ListAPIView):
    queryset = Contact.objects.all()
    serializer_class = FriendSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'user', 'unique_id', 'is_connected']


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comments.objects.all()
    serializer_class = Commentserializer


class CommentViewSetFilter(generics.ListAPIView):
    queryset = Comments.objects.all()
    serializer_class = Commentserializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post_id', 'comment_userid', 'comment_title']


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = Groupserializer


class GroupViewSetFilter(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = Groupserializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group_category',
                        'created_by', 'admin_name', 'group_name']


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = Pageserializer


class PageViewSetFilter(generics.ListAPIView):
    queryset = Page.objects.all()
    serializer_class = Pageserializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['page_category',
                        'created_by', 'admin_name', 'page_name']


class FriendPost(generics.ListCreateAPIView):
    model = Contact
    serializer_class = ContactsSerializer

    def get_queryset(self):
        queryset = Contact.objects.all()
        unique_id = self.request.query_params.get('unique_id')
        user = self.request.query_params.get('user')
        friend = self.request.query_params.get('friend')

        if unique_id:
            queryset = queryset.filter(unique_id=unique_id)
        elif user:
            queryset = queryset.filter(user=user)
        elif friend:
            queryset1 = queryset.filter(user=friend, is_connected=1)
            queryset2 = queryset.filter(registered_id=friend, is_connected=1)
            queryset = queryset1 | queryset2

        return queryset


class FriendReq(generics.ListCreateAPIView):
    model = Contact
    serializer_class = ContactsSerializer

    # Show all of the PASSENGERS in particular WORKSPACE
    # or all of the PASSENGERS in particular AIRLINE
    def get_queryset(self):
        queryset = Contact.objects.all()
        unique_id = self.request.query_params.get('unique_id')
        user = self.request.query_params.get('user')
        friend = self.request.query_params.get('friend')

        if unique_id:
            queryset = queryset.filter(unique_id=unique_id)
        elif user:
            queryset = queryset.filter(user=user)
        elif friend:
            queryset1 = queryset.filter(user=friend, is_connected=0)
            queryset2 = queryset.filter(registered_id=friend, is_connected=0)
            queryset = queryset1 | queryset2

        return queryset


class InviteReq(generics.ListCreateAPIView):
    model = Contact
    serializer_class = ContactsSerializer

    # Show all of the PASSENGERS in particular WORKSPACE
    # or all of the PASSENGERS in particular AIRLINE
    def get_queryset(self):
        queryset = Contact.objects.all()
        friend = self.request.query_params.get('friend')

        queryset1 = queryset.filter(user=friend, is_connected=1)
        queryset2 = queryset.filter(registered_id=friend, is_connected=1)
        queryset = queryset1 | queryset2

        pre_invitelist = requests.get(
            'http://deal:9002/deal/api/v1/users/invite/{}'.format(friend))
        data = []
        for pk in range(len(pre_invitelist)):
            if pre_invitelist[pk]['invite_from'] == friend:
                data.append(pre_invitelist[pk])
        print('pre_invitelist', data)
        return queryset


class Profilecheck(generics.ListCreateAPIView):
    model = Contact
    serializer_class = ContactsSerializer

    def get_queryset(self):
        queryset = Contact.objects.all()
        profileId, currentUserId = self.request.query_params.get(
            'profileId'), self.request.query_params.get('currentUserId')

        if profileId and currentUserId:
            print(profileId, currentUserId)
            queryset1 = queryset.filter(
                user=profileId, is_connected=1, registered_id=currentUserId)
            queryset2 = queryset.filter(
                user=currentUserId, is_connected=1, registered_id=profileId)

            queryset = queryset1 | queryset2

        return queryset


class FindFriends(generics.ListCreateAPIView):
    model = User
    serializer_class = UsersListSerializer

    def get_queryset(self):
        queryset = Contact.objects.all()
        friend = self.request.query_params.get('friend')

        if friend:
            queryset1 = Contact.objects.filter(
                profileId=friend)
            queryset2 = Contact.objects.filter(
                registered_id=friend)
            # queryset1 = queryset.filter(profileId=friend, is_connected=1)
            # queryset2 = queryset.filter(registered_id=friend, is_connected=1)
            # queryset = queryset1 | queryset2
            friends = queryset1 | queryset2

        friendsId = []
        for pk in friends:
            print(pk.registered_id, pk.profileId)
            friendsId.append(pk.registered_id)
            friendsId.append(pk.profileId)

        suggestUser = User.objects.all()
        obj = [pk for pk in suggestUser if pk.id not in friendsId]
        print(obj)
        return obj

        # return suggestUser


# def FriendSuggetion(friendsId):
#     suggestUser = User.objects.all()
#     obj = [pk for pk in suggestUser if pk.id not in friendsId]
#     print(obj)
#     return obj
