from django.contrib import admin
from .models import *

# Register your models here.
class ArtPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'title', 'created_by')

admin.site.register(UserFollowers)
admin.site.register(UserArt, ArtPostAdmin)