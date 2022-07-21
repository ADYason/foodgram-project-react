from django.contrib.auth.hashers import check_password
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, permissions, status,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscription, User
from .filters import IngredientFilter
from .mixins import (CreateRetriveViewSet, CreateDeleteViewSet,
                     ListRetriveViewSet)
from .paginators import StandardResultsSetPagination
from .permissions import IsAuthorStaffOrReadOnly
from .serializers import (FavoritesSerializer,
                          IngredientsListRetriveSerializer, RecipeSerializer,
                          RegistrationSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserRetrieveSerializer, UserSubscriptionSerializer,
                          RecipeToRepresentationSerializer)


class TagListRetriveViewSet(ListRetriveViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorStaffOrReadOnly, )
    lookup_field = 'id'
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_favorited is not None:
            queryset = queryset.filter(recipe_favorites__user=user)
        if is_in_shopping_cart is not None:
            queryset = queryset.filter(recipe_shoppingcart__user=user)
        return queryset.order_by('-pub_date')

    @action(
        detail=False,
        suffix=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        if shopping_cart.count() < 1:
            data = {'message': 'Корзина пуста'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        filename = 'shopping_cart.txt'
        ings = {}
        data = []
        ingredients = shopping_cart.values_list(
            'recipe__recipe_to_ingredient__ingredient__name',
            'recipe__recipe_to_ingredient__ingredient__measurement_unit'
        ).annotate(amount=Sum('recipe__recipe_to_ingredient__amount'))
        for ingredient in ingredients:
            name = ingredient[0]
            amount = ingredient[2]
            measure = ingredient[1]
            ings[name] = [measure, amount]
            if name in ings:
                ings[name][1] += amount
            else:
                ings[name] = [measure, amount]
        for key, value in ings.items():
            result = f'{key}({value[0]}) - {value[1]}, '
            data.append(result)
        response = HttpResponse(data, content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(filename))
        return response


class ShoppingCartViewSet(CreateDeleteViewSet):
    serializer_class = ShoppingCartSerializer
    queryset = ShoppingCart.objects.all()

    def get_queryset(self):
        recipe = get_object_or_404(
            Recipe,
            pk=self.kwargs.get('id'),
        )
        return ShoppingCart.objects.filter(recipe=recipe)

    def create(self, request, *args, **kwargs):
        pk = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
        except IntegrityError:
            data = {'message': 'Добавить рецеп в корзину можно только 1 раз.'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        serializer = RecipeToRepresentationSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            ShoppingCart.objects.get(user=request.user, recipe=recipe).delete()
        except ShoppingCart.DoesNotExist:
            data = {'message': 'Такого рецепта нет в корзине'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(CreateDeleteViewSet):
    serializer_class = FavoritesSerializer
    queryset = Favorite.objects.all()

    def get_queryset(self):
        recipe = get_object_or_404(
            Recipe,
            pk=self.kwargs.get('id'),
        )
        return Favorite.objects.filter(recipe=recipe)

    def create(self, request, *args, **kwargs):
        pk = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            Favorite.objects.create(user=request.user, recipe=recipe)
        except IntegrityError:
            data = {
                'message': 'Добавить рецепт в избранное можно только 1 раз.'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        serializer = RecipeToRepresentationSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            Favorite.objects.get(user=request.user, recipe=recipe).delete()
        except Favorite.DoesNotExist:
            data = {'message': 'Такого рецепта нет в корзине'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientsViewSet(ListRetriveViewSet):
    serializer_class = IngredientsListRetriveSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    search_fields = ('name', )


class UserCreateRetriveViewSet(CreateRetriveViewSet):
    serializer_class = UserRetrieveSerializer
    queryset = User.objects.all()
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = (permissions.IsAuthenticated, )
        if self.action == 'create':
            self.permission_classes = (permissions.AllowAny, )
        return super(UserCreateRetriveViewSet, self).get_permissions()

    def create(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        suffix=False,
        methods=['GET'],
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        user = request.user
        serializer = UserRetrieveSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        suffix=False,
        methods=['POST'],
        url_path='set_password',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_password(self, request):
        user = request.user
        if not (request.data.get('current_password') and
           request.data.get('new_password')):
            response = Response(status=status.HTTP_400_BAD_REQUEST)
            response.data = {'message': 'предоставленные данные неполны'}
            return response
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if not check_password(current_password, user.password):
            response = Response(status=status.HTTP_400_BAD_REQUEST)
            response.data = {'message': 'Cтарый пароль неправильный'}
            return response
        new_data = {'password': f'{new_password}'}
        serializer = RegistrationSerializer(user, data=new_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        suffix=False,
        methods=['GET'],
        url_path='subscriptions',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(
            subscriber=request.user)
        data = []
        if subscriptions is not None:
            for subscription in subscriptions:
                data.append(subscription.author)
        page = self.paginate_queryset(data)
        if page is not None:
            serializer = UserSubscriptionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserSubscriptionSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscriptionViewSet(CreateDeleteViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()

    def get_queryset(self):
        author = get_object_or_404(
            User,
            pk=self.kwargs.get('id'),
        )
        return Subscription.objects.filter(author=author)

    def create(self, request, *args, **kwargs):
        pk = self.kwargs.get('id')
        author = get_object_or_404(User, id=pk)
        try:
            Subscription.objects.create(
                subscriber=request.user,
                author=author
            )
        except IntegrityError:
            response = Response(status=status.HTTP_400_BAD_REQUEST)
            response.data = {'message': 'Подписаться можно только 1 раз.'}
            return response
        serializer = UserSubscriptionSerializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get('id')
        author = get_object_or_404(User, id=pk)
        try:
            Subscription.objects.get(
                author=author, subscriber=request.user).delete()
        except Subscription.DoesNotExist:
            data = {'message': 'Вы не подписаны на этого пользователя'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
