from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe

from .models import Subscriptions, User


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
