from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from foodgram.models import (Tag, Ingredient, Recipe,
                             Favorite, ShoppingCart, RecipeIngredients)
from users.models import User, Subscribe
from djoser.serializers import UserCreateSerializer


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'password')


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed')

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        if self.context.get('request'):
            user = self.context.get('request').user
            if user.is_anonymous:
                return False
            return Subscribe.objects.filter(user=user,
                                            following=obj.id).exists()
        return False


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = ShoppingCart


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['name', 'color', 'slug', 'id']
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientsRecipeSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredients


class IngredientRecipeSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredients


class GetRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(
        'get_ingredients'
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients_data = RecipeIngredients.objects.filter(recipe=obj)
        ingredients = IngredientsRecipeSerializer(ingredients_data,
                                                  many=True).data
        return ingredients

    def get_is_favorited(self, obj):
        if self.context.get('request'):
            request_user = self.context.get('request').user
            if request_user.is_anonymous:
                return False
            return Favorite.objects.filter(user=request_user,
                                           recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request'):
            request_user = self.context.get('request').user
            if request_user.is_anonymous:
                return False
            return ShoppingCart.objects.filter(user=request_user,
                                               recipe=obj).exists()
        return False


class PostRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredient_recipes')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
        )

    def validate_ingredients(self, value):
        ingredient_data = value
        if not ingredient_data:
            raise serializers.ValidationError({
                'Нужен хотя бы один ингредиент!'
            })
        ingredients_list = []
        for ingredient in ingredient_data:
            ingredient_id = ingredient['ingredient']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'Ингридиенты не могут повторяться!'
                })
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError({
                    'Количество ингредиента должно быть больше 0!'
                })
            ingredients_list.append(ingredient_id)
        return value

    def validate_tags(self, value):
        tags_data = value
        if not tags_data:
            raise serializers.ValidationError({
                'Нужно выбрать хотя бы один тег!'
            })
        tags_list = []
        for tag in tags_data:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'Теги должны быть уникальными!'
                })
            tags_list.append(tag)
        return value

    def add_ingredients(self, ingredient_data, recipe):
        for ingredient in ingredient_data:
            ingredient_id = ingredient['ingredient']
            amount = ingredient['amount']
            RecipeIngredients.objects.create(
                ingredient=ingredient_id,
                recipe=recipe,
                amount=amount
            )

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredient_recipes')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.add_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredient_recipes')
        instance.tags.set(tags_data)
        instance.image = validated_data.get(
            'image', instance.image
        )
        instance.name = validated_data.get(
            'name', instance.name
        )
        instance.text = validated_data.get(
            'text', instance.text
        )
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.ingredients.clear()
        self.add_ingredients(ingredients_data, instance)
        instance.save()
        return instance


class SubscriptionSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed'
    )
    recipes_count = serializers.SerializerMethodField(
        'get_recipes_count'
    )
    recipes = serializers.SerializerMethodField(
        'get_recipes'
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes_count', 'recipes')

    def get_is_subscribed(self, obj):
        if self.context.get('request'):
            user = self.context.get('request').user
            if user.is_anonymous:
                return False
            return Subscribe.objects.filter(
                user=user,
                following=obj.id).exists()
        return False

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        serializer = GetRecipeSerializer(recipes, many=True)
        return serializer.data


class SubscribeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)

    class Meta:
        model = Subscribe
        fields = ('user', 'following')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'following')
            )
        ]

    def validate(self, value):
        if self.context.get('request').user == value:
            raise serializers.ValidationError({
                'Нельзя подписаться на себя!'
            })


class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    recipe = GetRecipeSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [

            serializers.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def create(self, validated_data):
        return Favorite.objects.create(**validated_data)
