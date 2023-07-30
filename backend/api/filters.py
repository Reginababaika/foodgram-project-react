from django_filters.rest_framework import FilterSet, filters
from foodgram.models import Ingredient, Recipe
from users.models import User


class RecipeFilter(FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        return queryset.filter(
            in_favorite__user=self.request.user
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        return queryset.filter(
            in_shopping_list__user=self.request.user
        )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
