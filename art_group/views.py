from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializer import *
from art_group.models import *
from django.db.models import Q
from art_app.user_notification import *
from art_app.models import *


# Create your views here.
class AllGroups(APIView):
    def get(self, request):
        query = Group.objects.all()
        serializer = GroupSerializer(query, many=True)
        return Response(serializer.data)


class GroupView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        query = Group.objects.filter(id=pk)
        serializer = GroupDetailSerializer(query, many=True)
        return Response(serializer.data)

    def post(self, request, formate=None):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupSlugView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, slug):
        query = Group.objects.filter(slug=slug)
        serializer = GroupDetailSerializer(query, many=True)
        return Response(serializer.data)


class GroupFilterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        request_type = request.data['type']
        query = None

        if request_type == 'admin':
            query = Group.objects.filter(created_by=request.data['user'])

        elif request_type == 'all':
            query = Group.objects.all().order_by('-id')

        elif request_type == 'user':
            query_group = Group.objects.filter(Q(member__in=request.data['user']) |
                                         Q(created_by=request.data['user'])).order_by('-id')
            gid = list(set(i.id for i in query_group))
            query = Group.objects.filter(pk__in=gid)

        serializer = GroupSerializer(query, many=True)
        return Response(serializer.data)


# class GroupPostView(APIView):
#
#     def get(self, request, pk):
#         query = GroupPost.objects.filter(group=pk)
#         serializer = GroupPostSerializer(query, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = GroupPostSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors)


class GroupCommentView(APIView):
    def get(self, request, pk):
        query = PostComment.objects.filter(id=pk)
        serializer = GroupPostCommentSerializer(query)
        return Response(serializer.data)

    def post(self, request):
        serializer = GroupPostCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            query = GroupPost.objects.get(id=request.data['post'])
            query.comment.add(serializer.data['id'])
            query.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def put(self, request):
        query = PostComment.objects.get(id=request.data['comment_id'])
        serializer = GroupPostCommentSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def delete(self, request, pk):
        query = PostComment.objects.filter(id=pk).delete()
        ctx = {'message': 'Comment deleted successfully.'}
        return Response(ctx)


class GroupLikesView(APIView):
    def get(self, request, pk):
        query = PostLike.objects.filter(id=pk)
        serializer = GroupPostLikeSerializer(query)
        return Response(serializer.data)

    def post(self, request):
        serializer = GroupPostLikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            query = GroupPost.objects.get(id=request.data['post'])
            query.likes.add(serializer.data['id'])
            query.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def put(self, request):
        query = PostLike.objects.get(id=request.data['likes_id'])
        serializer = GroupPostLikeSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def delete(self, request, pk):
        query = PostLike.objects.filter(id=pk).delete()
        ctx = {'message': 'Removed Like.'}
        return Response(ctx)


class GroupInviteView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = GroupInvite.objects.filter(user=request.user)
        serializer = GroupInviteDetailSerializer(query, many=True)
        return Response(serializer.data)

    def post(self, request):
        group = Group.objects.filter(id=request.data['group'], member=request.data['user'])
        serializer = GroupInviteSerializer(data=request.data)
        if serializer.is_valid():
            if group:
                print(group)
                return Response(serializer.data)
            serializer.save()
            try:
                group_pk = request.data['group']
                message = f'{request.user.first_name} {request.user.last_name} is invite you to join {Group.objects.get(pk=group_pk).name} Group.'
                notice_user = request.data['user']
                notice = {
                    'notice_user': notice_user,
                    'message': message
                }
                response_notice = UserNotificationSerializer(data=notice)
                if response_notice.is_valid():
                    response_notice.save()
                print(response_notice)
            except:
                pass
            return Response(serializer.data)
        return Response(serializer.errors)


class GroupMemberView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, group_id):
        query = Group.objects.filter(id=group_id, member=request.user)
        if query:
            ctx = {'message': 'Already a member.', 'blob': True}
            return Response(ctx)
        ctx = {'message': 'Not a member.', 'blob': False}
        return Response(ctx)

    def post(self, request):
        group = Group.objects.filter(id=request.data['group'], member=request.user)
        if group:
            ctx = {'message': 'Already a member.', 'blob': True}
            return Response(ctx)
        query = Group.objects.get(id=request.data['group'])
        query.member.add(request.user)
        query.save()
        ctx = {'message': f'Member Added to the group.', 'blob': True}
        return Response(ctx)

    def put(self, request):
        group = Group.objects.filter(id=request.data['group'], member=request.user)
        if group:
            query = Group.objects.get(id=request.data['group'])
            query.member.remove(request.user)
            query.save()
            ctx = {'message': f'Member Removed from the group.', 'blob': True}
            return Response(ctx)

        ctx = {'message': 'Already not a member.', 'blob': True}
        return Response(ctx)


class GroupPostView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = UserArt.objects.filter(created_by=request.user)
        serializers = GroupPostDetailSerializer(query, many=True)
        return Response(serializers.data)


class PostView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        query = UserArt.objects.filter(group=id)
        serializers = GroupPostDetailSerializer(query, many=True)
        return Response(serializers.data)


class InviteSearch(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, group, keyword):
        query = Group.objects.get(pk=group)
        member = [i.id for i in query.member.all()]
        user = User.objects.filter(Q(first_name__icontains=keyword)).exclude(pk__in=member)
        serializers = UserSerializer(user, many=True)
        return Response(serializers.data)
