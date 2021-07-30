import threading
from django.db.models import Count, Sum, Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from rback.instance import db_back_up
from authentication.models import User

class DbBackUp(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request, format=None):

        t = threading.Thread(target=db_back_up)
        t.setDaemon(True)
        t.start()
        return Response(status=HTTP_200_OK)


class TotalStatsView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request, format=None):
        total_online = Count('connection_status', filter=Q(connection_status='O'))
        stats = User.objects.aggregate(total_users=Count('id'), total_connections=Sum('connection_sent') + Sum('connection_received'),
                                       total_deals=Sum('deal_requested') + Sum('deal_accepted') + Sum('deal_proposed'),
                                       total_online=total_online)

        return Response(status=HTTP_200_OK, data=stats)