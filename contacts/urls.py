from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers

from contacts.views import (
    Contacts, ContactDetail, MyConnectionList, Postfilter,
    PostViewSet, FriendsViewSet, FriendslistViewSet,
    CommentViewSet, CommentViewSetFilter, GroupViewSet,
    GroupViewSetFilter, PageViewSet, PageViewSetFilter,
    FriendPost, FriendReq, InviteReq, Profilecheck, FindFriends
)

router = routers.DefaultRouter()
router.register(r'post/create', PostViewSet)
router.register(r'friends', FriendsViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'user/group', GroupViewSet)
router.register(r'user/page', PageViewSet)
# url
urlpatterns = [
    path('api/v1/contacts', Contacts.as_view(), name='contact-list'),
    path('api/v1/contacts/<int:pk>',
         ContactDetail.as_view(), name='contact-detail'),
    path('api/v1/myconnection', MyConnectionList.as_view(),
         name='myconnection-list'),
    path('api/v1/post/filter', Postfilter.as_view()),
    path('api/v1/user/friends', FriendslistViewSet.as_view()),
    path('api/v1/user/post/comments', CommentViewSetFilter.as_view()),
    path('api/v1/user/group/filter', GroupViewSetFilter.as_view()),
    path('api/v1/user/page/filter', PageViewSetFilter.as_view()),
    path('api/v1/user/postfriend/filter', FriendPost.as_view()),
    path('api/v1/user/postfriend/filter/req', FriendReq.as_view()),
    path('api/v1/user/postfriend/filter/invite', InviteReq.as_view()),
    path('api/v1/user/profile/privacy', Profilecheck.as_view()),
    url(r'^api/v1/', include(router.urls)),
    path('api/v1/user/find/filter', FindFriends.as_view()),
]
