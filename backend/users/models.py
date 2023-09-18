from django.db import models
from django.contrib.auth.models import AbstractUser

from recipes.constants import USERNAME_NAME, EMAIL


class User(AbstractUser):
    username = models.CharField(
        'Никнейм', max_length=USERNAME_NAME, unique=True
    )
    email = models.EmailField(
        'Почта', max_length=EMAIL, unique=True
    )
    first_name = models.CharField(
        'Имя', max_length=USERNAME_NAME
    )
    last_name = models.CharField(
        'Фамилия', max_length=USERNAME_NAME
    )
    password = models.CharField(
        'Пароль', max_length=USERNAME_NAME
    )

    class Meta:
        verbose_name = 'Пользователь'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe'
            )
        ]
        verbose_name = 'Подписка'
