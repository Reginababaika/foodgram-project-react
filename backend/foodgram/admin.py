from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredients, ShoppingCart, Favorite, Tag

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredients)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
