from rest_framework import routers
from django.urls import path, include

from api.views import (TagViewSet, RecipeViewSet,
                       IngredientViewSet, FavoriteViewSet,
                       SubscriptionsViewSet, SubscribeViewSet,
                       SchoppingCartViewSet, DownloadCartViewSet)


routerv1 = routers.DefaultRouter()
routerv1.register(r'tags', TagViewSet, basename='tags')
routerv1.register(r'recipes', RecipeViewSet, basename='recipes')
routerv1.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('recipes/<recipes_id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create', 'delete': 'delete'}),
         name='favorite'),
    path('users/subscriptions/',
         SubscriptionsViewSet.as_view({'get': 'list'})),
    path('users/<users_id>/subscribe/',
         SubscribeViewSet.as_view({'post': 'create', 'delete': 'delete'})),
    path('recipes/<recipes_id>/shopping_cart/',
         SchoppingCartViewSet.as_view({'post': 'create', 'delete': 'delete'})),
    path('recipes/download_shopping_cart/',
         DownloadCartViewSet.as_view({'get': 'download'})),
    path('', include(routerv1.urls))
]
