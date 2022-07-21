from rest_framework import mixins, viewsets, permissions


class CreateRetriveViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    lookup_field = 'id'


class CreateDeleteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
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
