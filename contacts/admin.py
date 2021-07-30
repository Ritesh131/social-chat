from django.contrib import admin

from contacts.models import Contact


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile_no', 'email', 'unique_id', 'user')


admin.site.register(Contact, ContactAdmin)
