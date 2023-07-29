from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.permissions import SAFE_METHODS
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework import permissions, filters
from djoser.views import UserViewSet

from foodgram.models import (Ingredient, Tag, Recipe,
                             ShoppingCart, Favorite, RecipeIngredients)
from users.models import User, Subscribe
from .serializers import (TagSerializer, IngredientSerializer,
                          UserSerializer, FavoriteSerializer,
                          IngredientsRecipeSerializer)
from .serializers import (GetRecipeSerializer, PostRecipeSerializer,
                          SubscribeSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer)
from .filters import IngredientFilter, RecipeFilter


class ShoppingCartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    serializer_class = ShoppingCartSerializer
    lookup_field = 'id'
    queryset = ShoppingCart.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]

    def create(self, serializer, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shopping_cart = ShoppingCart.objects.create(
            user=self.request.user, recipe=recipe)
        serializer = self.get_serializer(shopping_cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeIngredientsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    lookup_field = 'id'
    queryset = RecipeIngredients.objects.all()
    serializer_class = IngredientsRecipeSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    lookup_field = 'id'
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return GetRecipeSerializer
        else:
            return PostRecipeSerializer

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorites(self, request):
        queryset = Recipe.objects.filter(
            in_favorite__user=request.user.id)
        page = self.paginate_queryset(queryset)
        serializer = GetRecipeSerializer(page,
                                         context={'request': request},
                                         many=True)
        return self.response(serializer.data)

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients_list = Recipe.objects.filter(
            in_shopping_list__user=request.user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(amount=Sum('ingredient_recipes__amount'))
        shopping_list = []
        for ingredient in ingredients_list:
            shopping_list.append(
                f'{ingredient["ingredients__name"]} - {ingredient["amount"]}'
                f'{ingredient["ingredients__measurement_unit"]} \n')

        response = HttpResponse(shopping_list,
                                'Content-Type: text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.txt"')
        return response


class CustomUserViewSet(UserViewSet):
    permission_classes = [permissions.AllowAny, ]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user.id)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(page, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("recipe__id", "user__id")

    def create(self, serializer, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite = Favorite.objects.create(user=self.request.user,
                                           recipe=recipe)
        serializer = self.get_serializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user.id
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("following__id", "user__id")

    def create(self, serializer, user_id):
        following = get_object_or_404(User, id=user_id)
        subscribe = Subscribe.objects.create(user=self.request.user,
                                             following=following)
        serializer = self.get_serializer(subscribe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        user = request.user
        following = get_object_or_404(User, id=user_id)
        Subscribe.objects.filter(user=user,
                                 following=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
