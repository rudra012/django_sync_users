from django.contrib import admin

from account.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'is_online', 'no_of_connection', 'last_online')
    list_editable = ('is_online', 'no_of_connection')


admin.site.register(User, UserAdmin)
