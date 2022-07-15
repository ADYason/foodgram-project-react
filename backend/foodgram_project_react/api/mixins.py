from rest_framework import mixins, viewsets, permissions
from rest_framework.generics import get_object_or_404

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
        return recipe.recipe_shoppingcart.get()
