import os
import mimetypes
from pathlib import Path
mimetypes.add_type("text/css", ".css", True)
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
DB_DIR = Path(__file__).resolve().parent.parent


# ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     'default': {
#         # 'ENGINE': 'djongo',
#         # 'NAME': 'nextop',
#         # 'HOST': 'user_db',
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'se_users',
#         'USER': 'root',
#         'PASSWORD': 'root0987',
#         'HOST': 'user_db',
#         'PORT': '',
#     },
#     'deal_db': {
#         'NAME': 'se_deal',
#         'ENGINE': 'django.db.backends.mysql',
#         'USER': 'admin',
#         'HOST': 'deal_db',
#         'PASSWORD': 'admin123'
#     }
# }

# NOTIFICATION_HOST = 'http://notification:9005/'
# NOTIFICATION_API = 'notification/notifications'
