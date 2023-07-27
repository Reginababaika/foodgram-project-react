"""foodgram_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework import routers
from django.urls import include, path
from djoser.views import UserViewSet as DjoserViewSet
from .views import RecipeViewSet, TagViewSet, UserViewSet, IngredientViewSet
from .views import SubscribeViewSet, ShoppingCartViewSet, FavoriteViewSet


app_name = 'api'

router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('users', UserViewSet)
router.register(r'users/(?P<user_id>\d+)/subscribe',
                SubscribeViewSet, basename='subscribe')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                ShoppingCartViewSet, basename='shopping_cart')
router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                FavoriteViewSet, basename='favorite')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('users/set_password/',
         DjoserViewSet.as_view({'post': 'set_password'})),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
