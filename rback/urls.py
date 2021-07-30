from django.urls import path

from rback.views import DbBackUp, TotalStatsView

urlpatterns = [
    path('api/rback/db_backup', DbBackUp.as_view(), name="database-backup"),
    path('api/v1/total/stats', TotalStatsView.as_view(), name="total-stats")
]