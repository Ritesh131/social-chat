from django.contrib import admin
from art_group.models import *


# Register your models here.
class ArtGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'categoy', 'created_by', 'created_on')


class GroupPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'group')


class GroupInviteAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'is_invited', 'created_at')


admin.site.register(Group, ArtGroupAdmin)
admin.site.register(GroupInvite, GroupInviteAdmin)
admin.site.register(GroupPost, GroupPostAdmin)
