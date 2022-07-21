from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
    )
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'author', 'subscriber',
    )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionsAdmin)
