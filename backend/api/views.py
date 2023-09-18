from rest_framework import viewsets
from django.shortcuts import HttpResponse, get_object_or_404
from rest_framework import status
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from recipes.models import (Tag, Recipe, Ingredient, Favorite,
                            ShoppingCart, RecipeIngredient)
from users.models import User, Subscribe
from .serializers import (TagSerializer, RecipeSerializer,
                          RecipeCreateSerializer, IngredientSerializer,
                          FavoriteSerializer, ShortRecipeSerializer,
                          SubscriptionsSerializer, SubscribeSerializer,
                          SchoppingCartSerializer)
from .pagination import CustomPagination
from .filters import RecipeFilter


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Ingredient"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Tag"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipe"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    # def dispatch(self, request, *args, **kwargs):
    #     # return super().dispatch(request, *args, **kwargs)
    #     res = super().dispatch(request, *args, **kwargs)
    #     from django.db import connection
    #     print(len(connection.queries))
    #     for i in connection.queries:
    #         print('>>>>>', i['sql'])

    #     return res

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipeingredient_set__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Favorite"""
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['recipes_id'])
        serializer = ShortRecipeSerializer(recipe, data=request.data,
                                           context={"request": request})
        serializer.is_valid(raise_exception=True)
        if not Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response({'errors': 'Рецепт уже в избранном.'},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['recipes_id'])
        favorite = get_object_or_404(Favorite, user=request.user,
                                     recipe=recipe)
        favorite.delete()
        return Response({'detail': 'Рецепт удален из избранного'},
                        status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """Вьюсет - мои подписки"""
    serializer_class = SubscriptionsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class SubscribeViewSet(viewsets.ModelViewSet):
    """Вьюсет подписаться/отписаться """
    permission_classes = (IsAuthenticated,)

    def create(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['users_id'])
        serializer = SubscribeSerializer(author, data=request.data,
                                         context={"request": request})
        serializer.is_valid(raise_exception=True)
        if not Subscribe.objects.filter(user=request.user, author=author):
            Subscribe.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': 'Вы уже подписаны на автора'},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['users_id'])
        subscribe = get_object_or_404(Subscribe, user=request.user,
                                      author=author)
        subscribe.delete()
        return Response({'detail': 'Вы успешно отписались'},
                        status=status.HTTP_204_NO_CONTENT)


class SchoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет добавление/удаление списка покупок"""
    queryset = Favorite.objects.all()
    serializer_class = SchoppingCartSerializer

    def create(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['recipes_id'])
        serializer = ShortRecipeSerializer(recipe, data=request.data,
                                           context={"request": request})
        serializer.is_valid(raise_exception=True)
        if not ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response({'errors': 'Рецепт уже в списке покупок'},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['recipes_id'])
        favorite = get_object_or_404(ShoppingCart, user=request.user,
                                     recipe=recipe)
        favorite.delete()
        return Response({'detail': 'Рецепт удален из списка покупок'},
                        status=status.HTTP_204_NO_CONTENT)


class DownloadCartViewSet(viewsets.ModelViewSet):
    """Вьюсет скачивания списка покупок"""
    permission_classes = (IsAuthenticated,)

    def download(self, request):
        shopping_cart_list = ['Cписок покупок:']
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_recipe__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(ingredient_amount=Sum('amount'))
        )
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_cart_list.append(f'\n{name}({unit}) - {amount}')
        file = HttpResponse(shopping_cart_list, content_type='text/plain')
        return file
