from django.contrib import admin

from authentication.models import User, Country, PhoneNumberOtp


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'phone_code')


class UserAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name',
                                      'last_name', 'phone', 'is_active', 'country')}),
        ('Loging Info', {'fields': ('connection_status',)}),
        ('Stats Data', {'fields': ('connection_sent', 'connection_received',
                                   'deal_requested', 'deal_accepted', 'deal_proposed')})
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_active', 'connection_status',
                    'connection_sent', 'connection_received', 'deal_requested', 'deal_accepted', 'deal_proposed')


class PhoneNumberOtpAdmin(admin.ModelAdmin):
    list_display = ('otp', 'phone', 'is_verified', 'created_at', 'updated_at')


admin.site.register(Country, CountryAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(PhoneNumberOtp, PhoneNumberOtpAdmin)
