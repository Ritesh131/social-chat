from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializers import *
from .helpers import *
from rest_framework.response import Response
from rest_framework import status
from authentication.models import User
from authentication.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .user_notification import *

# Create your views here.


def index(request):
    return HttpResponse('work')


class ArtImagesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = UserArt.objects.filter(group=None)
        serializer = UserArtCommentSerializer(query, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        property_id = 1
        images = dict((request.data).lists())['craft']
        # Save UserArt
        flag = 1
        arr = []
        art_id = []
        for img_name in images:
            modified_data = modify_input_for_multiple_files(property_id,
                                                            img_name)
            file_serializer = ArtImagesSerializer(data=modified_data)
            if file_serializer.is_valid():
                file_serializer.save()
                arr.append(file_serializer.data)
            else:
                flag = 0
                arr.append(file_serializer.errors)

        if flag == 1:
            
            try:
                art_data = {
                    'title': request.data['title'],
                    'category': request.data['category'],
                    'art_images': [i['id'] for i in arr],  # art_id,
                    # 'inspired_by': request.data['inspired_by'],
                    'tag': request.data['tag'],
                    'description': request.data['description'],
                    'created_by': request.user.id,
                    'media_type': request.data['media_type'],
                    'group': request.data.get('group', ''),
                    'thumbnail': request.FILES['thumbnail']
                    }                    
            except:
                art_data = {
                    'title': request.data['title'],
                    'category': request.data['category'],
                    'art_images': [i['id'] for i in arr],  # art_id,
                    # 'inspired_by': request.data['inspired_by'],
                    'tag': request.data['tag'],
                    'description': request.data['description'],
                    'created_by': request.user.id,
                    'group': request.data.get('group', ''),
                    'media_type': request.data['media_type']
                }
                
            
            # img_list = [i['id'] for i in arr]
            # art_data = request.data
            # art_data['art_images'] = img_list
            # art_data['created_by'] = request.user.id

            serializer = UserArtSerializer(data=art_data)
            if serializer.is_valid():
                serializer.save()
                try:
                    art_title = request.data['title']
                    message = f'you have successfully created Art with title- {art_title}.'
                    notice_user = request.user.id
                    notice = {
                        'notice_user': notice_user,
                        'message': message
                    }
                    response_notice = UserNotificationSerializer(data=notice)
                    if response_notice.is_valid():
                        response_notice.save()
                    print(response_notice.errors)
                except Exception as e:
                    print(e)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(arr, status=status.HTTP_400_BAD_REQUEST)


class GetUserArt(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = UserArt.objects.filter(created_by=request.user.id)
        serializer = UserArtCommentSerializer(query, many=True)
        return Response(serializer.data)


class FollowersView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = UserFollowers.objects.filter(following_user_id=request.user.id)
        total_followers = len(query)
        serializer = FollowerFollowingDetailSerializer(query, many=True)
        return Response({'total_followers': total_followers, 'followers_data': serializer.data})

    def post(self, request, fomate=None):
        reqData = {}
        for key, value in request.data.items():
            print(key, value)
            reqData[key] = value
        reqData['user_id'] = request.user.id
        serializer = FollowersSerializer(data=reqData)
        if serializer.is_valid():
            serializer.save()
            try:
                message = f'{request.user.first_name} {request.user.last_name} is started following you.'
                notice_user = request.data['following_user_id']
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowingView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = UserFollowers.objects.filter(user_id=request.user.id)
        total_following = len(query)
        serializer = FollowerFollowingDetailSerializer(query, many=True)
        return Response({'total_following': total_following, 'following_data': serializer.data})


class FollowingArtView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = UserFollowers.objects.filter(Q(following_user_id=request.user.id) | Q(user_id=request.user.id))
        following_id = []
        serializer = FollowerDetailSerializer(query, many=True)
        for i in query:
            following_id.append(i.user_id.id)
            following_id.append(i.following_user_id.id)

        # for i in query2:
        #     following_id.append(i.following_user_id.id)
        #     following_id.append(i.user_id.id)

        feed_id = list(set(following_id))

        query_art = UserArt.objects.filter(created_by__id__in=feed_id).order_by('-id')
        serializer = UserArtCommentSerializer(query_art[0:10], many=True)
        return Response(serializer.data)


class ArtlikeView(APIView):
    def put(self, request, formate=None):
        query = UserArt.objects.get(id=request.data['art_id'])
        query_serializer = UserArtSerializer(query)
        art_likes = query_serializer.data['likes']
        art_likes.append(request.data['likeuser_id'])
        like_data = {
            'likes': art_likes
        }
        serializer = UserArtSerializer(query, data=like_data)
        if serializer.is_valid():
            serializer.save()
            res_query = UserArt.objects.get(id=request.data['art_id'])
            res_serializer = UserArtCommentSerializer(res_query)
            try:
                user = User.objects.get(id=request.data['likeuser_id'])
                print('user', user)
                message = f'{user.first_name} {user.last_name} liked your post - {query.title}.'
                print('message', message)
                notice_user = query.created_by.id
                notice = {
                    'notice_user': notice_user,
                    'message': message
                }
                response_notice = UserNotificationSerializer(data=notice)
                if response_notice.is_valid():
                    response_notice.save()
                print(response_notice.errors)
            except Exception as e:
                print(e)
            return Response(res_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, formate=None):
        query = UserArt.objects.get(id=request.data['art_id'])
        query_serializer = UserArtSerializer(query)
        query.likes.remove(request.data['likeuser_id'])
        query.save()
        res_query = UserArt.objects.get(id=request.data['art_id'])
        res_serializer = UserArtCommentSerializer(res_query)
        return Response(res_serializer.data)

class ArtCommentView(APIView):
    def post(self, request, formate=None):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            query = UserArt.objects.get(id=request.data['art_id'])
            query_serializer = UserArtSerializer(query)
            art_comment = query_serializer.data['comment']
            art_comment.append(serializer.data['id'])
            comment_data = {
                'comment': art_comment
            }
            art_serializer = UserArtSerializer(query, data=comment_data)
            if art_serializer.is_valid():
                art_serializer.save()
                print('art_serializer', art_serializer.data)
                res_query = UserArt.objects.get(id=request.data['art_id'])
                res_serializer = UserArtCommentSerializer(res_query)
                try:
                    user = User.objects.get(id=request.data['comment_user'])
                    comment = request.data['comment']
                    message = f'{user.first_name} {user.last_name} comment on your post ({query.title}) - {comment}. '
                    print('message', message)
                    notice_user = query.created_by.id
                    notice = {
                        'notice_user': notice_user,
                        'message': message
                    }
                    response_notice = UserNotificationSerializer(data=notice)
                    if response_notice.is_valid():
                        response_notice.save()
                    print(response_notice.errors)
                except Exception as e:
                    print(e)
                return Response(res_serializer.data)
            return Response(art_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FriendSuggetionView(APIView):
    def get(self, request, id):
        query = UserFollowers.objects.filter(following_user_id=id)
        query2 = UserFollowers.objects.filter(user_id=id)
        following_id = []
        serializer = FollowerDetailSerializer(query, many=True)
        for i in query:
            following_id.append(i.user_id.id)
            following_id.append(i.following_user_id.id)

        for i in query2:
            following_id.append(i.following_user_id.id)
            following_id.append(i.user_id.id)

        feed_id = list(set(following_id))
        user_query = User.objects.exclude(id__in=feed_id)
        serializer = UserSerializer(user_query, many=True)
        return Response(serializer.data)


class UserArtCountView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        art = UserArt.objects.filter(created_by=request.user)
        following = UserFollowers.objects.filter(
            following_user_id=request.user)
        followers = UserFollowers.objects.filter(user_id=request.user)

        return Response({'total_art': len(art), 'total_followers': len(following), 'total_following': len(followers)})


class CategoryArtView(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        query_art = UserArt.objects.filter(category=request.data['category'])
        serializer = UserArtCommentSerializer(query_art, many=True)
        return Response(serializer.data)


class ArtCategoryView(APIView):
    def get(self, request):
        category = Art_Category
        print(category, 'category')
        return Response({'category': category})


class DelTemp(APIView):

    def get(self, request, id):
        query = UserArt.objects.get(id=id).delete()
        return Response({'ata': 'deleted'})


class NotificationView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, id):
        query = UserNotification.objects.filter(notice_user=id).order_by('-id')
        serializer = UserNotificationSerializer(query, many=True)
        return Response(serializer.data)


class FriendProfileView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, id):
        query = User.objects.get(pk=id)
        serializer = UserSerializer(query)
        return Response(serializer.data)


class FriendFollowerView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, id):
        # get followers
        query_followers = UserFollowers.objects.filter(user_id=id)
        serializer_followers = FollowerFollowingDetailSerializer(query_followers, many=True).data
        
        # get following
        query_following = UserFollowers.objects.filter(following_user_id=id)
        serializer_following = FollowerFollowingDetailSerializer(query_following, many=True).data
        ctx = {
                'total_followers': len(query_following), 
                'followers_data': serializer_following,
                'total_following': len(query_followers),
                'following_data': serializer_followers,
            }
        
        return Response(ctx)


class FriendPostView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, id):
        query = UserArt.objects.filter(created_by=id)
        serializer = UserArtCommentSerializer(query, many=True)
        return Response(serializer.data)

