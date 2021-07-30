from django.urls import path
from .views import *

urlpatterns = [
    path('group/create', GroupView.as_view()),
    path('group/<int:pk>', GroupView.as_view()),
    path('slug/<slug>', GroupSlugView.as_view()),
    path('filter/keyword', GroupFilterView.as_view()),
    # path('post/create', GroupPostView.as_view()),
    path('post/get/<int:id>', PostView.as_view()),
    path('post/user/get', GroupPostView.as_view()),
    path('post/comment/<int:pk>', GroupCommentView.as_view()),
    path('post/comment/create', GroupCommentView.as_view()),
    path('post/likes/create', GroupLikesView.as_view()),
    path('post/likes/<int:pk>', GroupLikesView.as_view()),
    path('invite', GroupInviteView.as_view()),
    path('member', GroupMemberView.as_view()),
    path('member/<int:group_id>', GroupMemberView.as_view()),
    path('invite/search/<int:group>/<keyword>', InviteSearch.as_view())
]
