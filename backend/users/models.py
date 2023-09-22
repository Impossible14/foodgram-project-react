from django.db import models
from django.contrib.auth.models import AbstractUser

from recipes.constants import USERNAME_NAME, EMAIL


class User(AbstractUser):
    username = models.CharField(
        max_length=USERNAME_NAME,
        unique=True,
        verbose_name='Никнейм'
    )
    email = models.EmailField(
        max_length=EMAIL,
        unique=True,
        verbose_name='Почта'
    )
    first_name = models.CharField(
        max_length=USERNAME_NAME,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=USERNAME_NAME,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=USERNAME_NAME,
        verbose_name='Пароль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


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
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_subscribe'
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} {self.author}'
