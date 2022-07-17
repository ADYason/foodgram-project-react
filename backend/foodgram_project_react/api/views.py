from django.contrib.auth.hashers import check_password
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
from .mixins import (CreateRetriveViewSet, CreateViewSet, ListRetriveViewSet,
                     CartAndFavoriteViewSet)
from .paginators import StandardResultsSetPagination
from .permissions import IsAuthorStaffOrReadOnly
from .serializers import (FavoritesSerializer,
                          IngredientsListRetriveSerializer, RecipeSerializer,
                          RegistrationSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserRetrieveSerializer, UserSubscriptionSerializer)


class TagListRetriveViewSet(ListRetriveViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorStaffOrReadOnly, )
    lookup_field = 'id'
    pagination_class = StandardResultsSetPagination

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
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


class ShoppingCartViewSet(CartAndFavoriteViewSet):
    serializer_class = ShoppingCartSerializer
    queryset = ShoppingCart.objects.all()
    model = ShoppingCart


class FavoriteViewSet(CartAndFavoriteViewSet):
    serializer_class = FavoritesSerializer
    queryset = Favorite.objects.all()
    model = Favorite


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
        methods=['POST'],
        url_path='set_password',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_password(self, request):
        user = request.user
        if (request.data.get('current_password') and
           request.data.get('new_password')):
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
        methods=['GET'],
        url_path='subscriptions',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(
            subscriber=request.user)
        data = []
        data.append(subscriptions.author)
        page = self.paginate_queryset(data)
        if page is not None:
            serializer = UserSubscriptionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserSubscriptionSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscriptionViewSet(CreateViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()

    def get_queryset(self):
        author = get_object_or_404(
            Subscription,
            pk=self.kwargs.get('id'),
        )
        return author.author

    def create(self, request, *args, **kwargs):
        pk = self.kwargs.get('id')
        author = get_object_or_404(User, id=pk)
        Subscription.objects.get_or_create(
            subscriber=request.user,
            author=author
        )
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
