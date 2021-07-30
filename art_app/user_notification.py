from .models import *
from .serializers import *
from rest_framework.views import APIView

def UserNotificationView(data):
    serializer = UserNotificationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        print(serializer.data)
    print(serializer.errors)
