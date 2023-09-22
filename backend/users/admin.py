from django.contrib import admin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'date_joined'
    ]

    search_fields = [
        'username',
        'first_name',
        'last_name',
        'email'
    ]

    list_filter = [
        'username',
        'email'
    ]

    empty_value_display = '-Пусто-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'user',
        'author',
    ]

    search_fields = [
        'user',
        'author',
    ]
