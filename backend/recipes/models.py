from django.db import models
from django.core.validators import MinValueValidator

from users.models import User
from .constants import MAX_LENGHT, LEN_FOR_SLUG, MIN_SCORE


class Tag(models.Model):
    name = models.CharField(max_length=MAX_LENGHT)
    color = models.CharField(max_length=LEN_FOR_SLUG)
    slug = models.SlugField(max_length=MAX_LENGHT,
                            unique=True)

    class Meta:
        verbose_name = 'Тег'


class Recipe(models.Model):
    name = models.CharField(max_length=MAX_LENGHT)
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=True
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(
            MIN_SCORE, message='Минимальное время приготовление одна минута'),
        ],
    )
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=MAX_LENGHT)
    measurement_unit = models.CharField(max_length=MAX_LENGHT)

    class Meta:
        verbose_name = 'Ингредиент'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(
            MIN_SCORE, message='Минимальное количество 1'),
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент с рецептом'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]
        verbose_name = 'Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe'
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
        verbose_name = 'Список покупок'
