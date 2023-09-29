import re
from rest_framework import serializers, status
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from recipes.models import (Tag, Recipe,
                            RecipeIngredient, Ingredient,
                            Favorite, ShoppingCart)
from users.serializers import CustomUserSerializer
from users.models import User, Subscribe


class IngredientSerializer(serializers.ModelSerializer):
    """Ингредиент"""
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Тег"""
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Краткое отображение рецепта"""
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Ингредиент в рецепте"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    """Рецепт"""
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipeingredient_set',
                                             read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'image', 'name', 'text',
                  'cooking_time')
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Favorite.objects.filter(
                    user=request.user, recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=request.user, recipe=obj
                ).exists())


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Создание ингредиентов в рецепте"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание рецепта"""
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        fields = ('id', 'ingredients', 'tags', 'author', 'name', 'image',
                  'text', 'cooking_time')
        model = Recipe

    def validate(self, data):
        if not data:
            raise serializers.ValidationError(
                detail='Отсутствуют ингридиенты!',
                code=status.HTTP_400_BAD_REQUEST
            )
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    detail='Ингредиенты должны быть уникальны',
                    code=status.HTTP_400_BAD_REQUEST
                )
            ingredients_list.append(ingredient_id)
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    detail='Количество не может быть меньше одного',
                    code=status.HTTP_400_BAD_REQUEST
                )
        if data.get('cooking_time') <= 0:
            raise serializers.ValidationError(
                detail='Время должно быть больше нуля',
                code=status.HTTP_400_BAD_REQUEST
            )

        return data

    def validate_tags(self, value):
        if not value:
            raise ValidationError(
                detail='Нужно выбрать хотя бы один тег',
                code=status.HTTP_400_BAD_REQUEST
            )
        tags_list = []
        for tag in value:
            if tag in tags_list:
                raise ValidationError(
                    detail='Теги должны быть уникальными',
                    code=status.HTTP_400_BAD_REQUEST
                )
            tags_list.append(tag)
        return value

    def validate_name(self, value):
        if not re.search(r'[a-zA-Zа-яА-ЯёЁ]', value):
            raise ValidationError(
                detail='Нельзя создавать рецепты с названиями'
                'только из цифр и знаков',
                code=status.HTTP_400_BAD_REQUEST)
        return value

    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient_data in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(
            instance,
            context=context
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Избранное"""
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        read_only_fields = ('name',)


class SubscriptionsSerializer(CustomUserSerializer):
    """Подписки"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = User

    def get_recipes(self, obj):
        serializer = ShortRecipeSerializer(
            obj.recipes.all(),
            many=True,
            read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(CustomUserSerializer):
    """Подписаться - отписаться"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = User

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, obj):
        serializer = ShortRecipeSerializer(
            obj.recipes.all(),
            many=True,
            read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SchoppingCartSerializer(serializers.ModelSerializer):
    """Список покупок"""
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
