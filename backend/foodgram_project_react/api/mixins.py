from rest_framework import mixins, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from .serializers import RecipeToRepresentationSerializer
from recipes.models import Recipe


class CreateRetriveViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    lookup_field = 'id'


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


class CartAndFavoriteViewSet(CreateViewSet):
    def get_queryset(self):
        recipe = get_object_or_404(
            Recipe,
            pk=self.kwargs.get('id'),
        )
        return recipe.recipe_shoppingcart

    def create(self, request, *args, **kwargs):
        pk = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=pk)
        self.model.objects.get_or_create(user=request.user, recipe=recipe)
        serializer = RecipeToRepresentationSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            self.model.objects.get(user=request.user, recipe=recipe).delete()
        except self.model.DoesNotExist:
            data = {'message': 'Такого рецепта нет в корзине'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
