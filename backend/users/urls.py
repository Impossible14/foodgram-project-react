from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet


routerv1 = DefaultRouter()
routerv1.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(routerv1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
