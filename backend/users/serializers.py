from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer

from .models import User, Subscribe


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользователя"""
    is_subscribed = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Subscribe.objects.filter(
                    user=request.user, author=obj
                ).exists())


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя"""
    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')
        model = User
