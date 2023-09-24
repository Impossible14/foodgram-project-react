from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from colorfield.fields import ColorField

from users.models import User
from .constants import (MAX_LENGHT, LEN_FOR_COLOR, MIN_SCORE,
                        MAX_COOKING_TIME, MAX_AMOUNT)


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='Название'
    )
    color = ColorField(
        format='hex',
        max_length=LEN_FOR_COLOR,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=MAX_LENGHT,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=True,
        verbose_name='Картинка'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                MIN_SCORE,
                message='Минимальное время приготовление одна минута'),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message='максимальное время приготовление 1000 минут')
        ],
        verbose_name='Время готовки'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name='Ингедиенты'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='единица измерений')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты')
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                MIN_SCORE, message='Минимальное количество один'),
            MaxValueValidator(
                MAX_AMOUNT, message='Максимальное количество 10000'
            )
        ],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент с рецептом'
        verbose_name_plural = 'Ингредиенты с рецептами'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class BaseFavoriteShoppingCart(models.Model):
    """Абстрактная модель"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Favorite(BaseFavoriteShoppingCart):

    class Meta:
        default_related_name = 'favorite'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(BaseFavoriteShoppingCart):

    class Meta:
        default_related_name = 'shopping_recipe'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
