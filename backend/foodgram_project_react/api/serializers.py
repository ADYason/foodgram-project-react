import base64

from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorites, Ingredients, Recipe, RecipeIngredients,
                            RecipeTags, ShoppingCart, Tags)
from users.models import Subscriptions, User


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    color = serializers.CharField()
    slug = serializers.SlugField()

    class Meta:
        model = Tags
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ("id", "name", "measurement_unit", "amount", )


class IngredientsListRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class UserRetrieveSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            author=request.user, subscriber=obj).exists()


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserRetrieveSerializer(
        default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientSerializer(
        source="recipe_to_ingredient",
        many=True
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
            'cooking_time'
        )
        read_only_fields = (
            'id',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorites.objects.filter(
            user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()


class RecipeSerializer(serializers.ModelSerializer):
    author = UserRetrieveSerializer(
        default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        required=True,
        write_only=True,
        many=True,
        queryset=Tags.objects.all(),
    )
    image = serializers.ImageField(
        required=True,
    )
    name = serializers.CharField(
        required=True,
    )
    text = serializers.CharField(
        required=True,
    )
    cooking_time = serializers.IntegerField(
        required=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = (
            'id',
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.save()
        tags_data = []
        ingredients_data = []
        for tag in tags:
            RecipeTags.objects.create(recipe=recipe, tag=tag)
            tags_data.append(tag)
        for ingredient in ingredients:
            id = ingredient.get("id")
            amount = ingredient.get("amount")
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=id,
                amount=amount
            )
            ingredients_data.append(id)
        recipe.tags.add(*tags_data)
        recipe.ingredients.add(*ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().update(instance, validated_data)
        tags_data = []
        ingredients_data = []
        for tag in tags:
            RecipeTags.objects.create(recipe=recipe, tag=tag)
            tags_data.append(tag)
        for ingredient in ingredients:
            id = ingredient.get("id")
            amount = ingredient.get("amount")
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=id,
                amount=amount
            )
            ingredients_data.append(id)
        recipe.tags.add(*tags_data)
        recipe.ingredients.add(*ingredients_data)
        return recipe

    def to_internal_value(self, data):
        imgstr = data.get('image')
        format, imgstr = imgstr.split(';base64,')
        ext = format.split('/')[-1]
        image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        data['image'] = image
        return super(RecipeSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeToRepresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.HiddenField(
        default=RecipeToRepresentationSerializer()
    )

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe']
            )
        ]

    def validate_recipe(self, value):
        id = self.context['view'].kwargs.get('id')
        return get_object_or_404(Recipe, pk=id)


class FavoritesSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.HiddenField(
        default=RecipeToRepresentationSerializer()
    )

    class Meta:
        model = Favorites
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorites.objects.all(),
                fields=['user', 'recipe']
            )
        ]

    def validate_recipe(self, value):
        id = self.context['view'].kwargs.get('id')
        return get_object_or_404(Recipe, pk=id)


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
    )
    username = serializers.SlugField(
        required=True,
    )
    first_name = serializers.CharField(
        required=True,
    )
    last_name = serializers.CharField(
        required=True,
    )
    password = serializers.CharField(
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        read_only_fields = ('id', )

    def create(self, validated_data):
        if validated_data['username'] == 'me':
            raise serializers.ValidationError(
                'выберите другое username, недопустипмо использовать me')
        validated_data['password'] = make_password(
                                    validated_data.get('password'))
        return User.objects.create(**validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password')
        return data


class MyTokenObtainSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True,
        style={"input_type": "password"},
    )
    email = serializers.EmailField(
        required=True,
    )

    class Meta:
        model = User
        fields = ('password', 'email')


class RecipeToUser(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeToUser(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            author=request.user, subscriber=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


class SubscriptionSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=UserSubscriptionSerializer()
    )
    subscriber = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Subscriptions
        fields = ('subscriber', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=['subscriber', 'author']
            )
        ]

    def validate_author(self, value):
        id = self.context['view'].kwargs.get('id')
        return get_object_or_404(User, pk=id)
