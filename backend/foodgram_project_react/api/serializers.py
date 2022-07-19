import base64

from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, ValidationError

from .utilits import tag_operator, ingredient_operator
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from users.models import Subscription, User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
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
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount', )


class IngredientsListRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
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
        return Subscription.objects.filter(
            author=request.user, subscriber=obj).exists()


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserRetrieveSerializer(
        default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientSerializer(
        source='recipe_to_ingredient',
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
        return Favorite.objects.filter(
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
    ingredients = IngredientAmountSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        required=True,
        write_only=True,
        many=True,
        queryset=Tag.objects.all(),
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

    def validate_ingredients(self, value):
        for ingredient in value:
            count = 0
            for same_ing in value:
                if same_ing == ingredient:
                    count += 1
            if count > 1:
                raise ValidationError('дубликат ингредиента')
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.save()
        tags_data = []
        ingredients_data = []
        ingredient_create = []
        tag_operator(tags, RecipeTag, tags_data, recipe)
        ingredient_operator(
            ingredients, RecipeIngredient,
            recipe, ingredients_data,
            ingredient_create, ValidationError
        )
        RecipeIngredient.objects.bulk_create(ingredient_create)
        recipe.tags.add(*tags_data)
        recipe.ingredients.add(*ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().update(instance, validated_data)
        tags_data = []
        ingredients_data = []
        ingredient_create = []
        tag_operator(tags, RecipeTag, tags_data, recipe)
        ingredient_operator(
            ingredients, RecipeIngredient,
            recipe, ingredients_data,
            ingredient_create, ValidationError
        )
        RecipeIngredient.objects.bulk_create(ingredient_create)
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


class FavoritesSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.HiddenField(
        default=RecipeToRepresentationSerializer()
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe']
            )
        ]


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
        style={'input_type': 'password'},
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

    def validate_username(self, value):
        lower_username = value.lower()
        if lower_username == 'me':
            raise serializers.ValidationError(
                'выберите другое username, недопустипмо использовать me')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'выберите другое username, этот уже занят')
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(
                                    validated_data.get('password'))
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['password'] = make_password(
                                    validated_data.get('password'))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password')
        return data


class TokenObtainSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
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
        return Subscription.objects.filter(
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
        model = Subscription
        fields = ('subscriber', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['subscriber', 'author']
            )
        ]
