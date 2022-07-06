import django_filters
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, mixins, pagination, permissions, status,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Favorites, Ingredients, Recipe, ShoppingCart, Tags
from .permissions import IsAuthorStaffOrReadOnly
from .serializers import (FavoritesSerializer,
                          IngredientsListRetriveSerializer, RecipeSerializer,
                          RecipeToRepresentationSerializer,
                          ShoppingCartSerializer, TagSerializer)


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CreateViewSet(mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    permission_classes = (
        permissions.IsAuthenticated,
    )


class ListRetriveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    lookup_field = 'id'


class TagListRetriveViewSet(ListRetriveViewSet):
    serializer_class = TagSerializer
    queryset = Tags.objects.all()


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
        for item in shopping_cart:
            ingredients = item.recipe.ingredients.all()
            for ingredient in ingredients:
                name = ingredient.name
                measure = ingredient.measurement_unit
                amount = item.recipe.recipe_to_ingredient.get(
                    recipe=item.recipe.id).amount
                if name in ings:
                    ings[name][1] += amount
                else:
                    ings[name] = [measure, amount]
        for key, value in ings.items():
            result = f'{key}({value[0]}) - {value[1]}'
            data.append(result)
        response = HttpResponse(data, content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(filename))
        return response


class ShoppingCartViewSet(CreateViewSet):
    serializer_class = ShoppingCartSerializer
    queryset = ShoppingCart.objects.all()

    def get_queryset(self):
        recipe = get_object_or_404(
            Recipe,
            pk=self.kwargs.get('id'),
        )
        return recipe.recipe_shoppingcart.get()

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=id)
        serializer = RecipeToRepresentationSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=id)
        try:
            ShoppingCart.objects.get(user=request.user, recipe=recipe).delete()
        except ObjectDoesNotExist:
            data = {'message': 'Такого рецепта нет в корзине'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoritesViewSet(CreateViewSet):
    serializer_class = FavoritesSerializer
    queryset = Favorites.objects.all()

    def get_queryset(self):
        recipe = get_object_or_404(
            Recipe,
            pk=self.kwargs.get('id'),
        )
        return recipe.recipe_favorites.get()

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=id)
        serializer = RecipeToRepresentationSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=id)
        try:
            Favorites.objects.get(user=request.user, recipe=recipe).delete()
        except ObjectDoesNotExist:
            data = {'message': 'Такого рецепта нет в избранном'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='icontains')

    class Meta:
        model = Ingredients
        fields = ('name',)


class IngredientsViewSet(ListRetriveViewSet):
    serializer_class = IngredientsListRetriveSerializer
    queryset = Ingredients.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    search_fields = ('name', )
