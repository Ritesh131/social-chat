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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from notification.notification import NotificationWorker

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Users API",
        default_version='v1',
        description="Users API",
        # terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="vishnu@spliceglobal.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/api-auth/', include('rest_framework.urls')),
    path('user/', include('authentication.urls')),
    path('user/', include('contacts.urls')),
    path('user/', include('rback.urls')),
    path('art/', include('art_app.urls')),
    path('message/', include('messanger.urls')),
    path('stream/', include('stream_app.urls')),
    path('payment/', include('payment_app.urls')),
    path('art/group/', include('art_group.urls')),
    # path('swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('user/swagger/', schema_view.with_ui('swagger',
                                              cache_timeout=0), name='schema-swagger-ui'),
    path('user/redoc/', schema_view.with_ui('redoc',
                                            cache_timeout=0), name='schema-redoc'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Start notification worker
notification_worker = NotificationWorker()
notification_worker.start()
