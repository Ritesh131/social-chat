"""users URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework import routers
from .views import *

# router = routers.DefaultRouter()
# router.register(r'users', AddFollowers)
# urlpatterns = router.urls

urlpatterns = [
    # path('', include(router.urls)),
    path('user/art/create', ArtImagesView.as_view()),
    path('count', UserArtCountView.as_view()),
    path('user/art', GetUserArt.as_view()),
    path('user/followers/add', FollowersView.as_view()),
    path('user/followers', FollowersView.as_view()),
    path('user/following', FollowingView.as_view()),
    path('user/followers/feed', FollowingArtView.as_view()),
    path('user/art/like', ArtlikeView.as_view()),
    path('user/art/comment', ArtCommentView.as_view()),
    path('user/following/suggetion/<int:id>', FriendSuggetionView.as_view()),
    path('category', CategoryArtView.as_view()),
    path('categorylist', ArtCategoryView.as_view()),
    path('del/<int:id>', DelTemp.as_view()),
    path('notification/user/<int:id>', NotificationView.as_view()),
    # another user detail
    path('user/profile/detail/<int:id>', FriendProfileView.as_view()),
    path('user/friends/detail/<int:id>', FriendFollowerView.as_view()),
    path('user/friends/post/<int:id>', FriendPostView.as_view())
]
