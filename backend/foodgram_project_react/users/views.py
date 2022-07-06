from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.views import CreateViewSet, StandardResultsSetPagination

from .models import Subscriptions, User
from .serializers import (RegistrationSerializer,
                          SubscriptionSerializer, UserRetrieveSerializer,
                          UserSubscriptionSerializer)


class CreateRetriveViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    lookup_field = 'id'


class UserCreateRetriveViewSet(CreateRetriveViewSet):
    serializer_class = UserRetrieveSerializer
    queryset = User.objects.all()
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = (permissions.IsAuthenticated, )
        if self.action == "create":
            self.permission_classes = (permissions.AllowAny, )
        return super(UserCreateRetriveViewSet, self).get_permissions()

    def create(self, request):
        username = request.data.get('username')
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            User.objects.create(
                username=username,
            )
        except IntegrityError:
            response = Response(status=status.HTTP_400_BAD_REQUEST)
            response.data = {'message': 'username уже занят'}
            return response
        User.objects.get(
            username=username,
        ).delete()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['GET'],
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        username = request.user.username
        user = get_object_or_404(User, username=username)
        serializer = UserRetrieveSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['POST'],
        url_path='set_password',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_password(self, request):
        username = request.user.username
        user = get_object_or_404(User, username=username)
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
        subscriptions = Subscriptions.objects.filter(
            subscriber=request.user).all()
        data = []
        for item in subscriptions:
            data.append(item.author)
        page = self.paginate_queryset(data)
        if page is not None:
            serializer = UserSubscriptionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserSubscriptionSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscriptionViewSet(CreateViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subscriptions.objects.all()

    def get_queryset(self):
        author = get_object_or_404(
            Subscriptions,
            pk=self.kwargs.get('id'),
        )
        return author.author.get()

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        id = self.kwargs.get('id')
        author = get_object_or_404(User, id=id)
        serializer = UserSubscriptionSerializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        author = get_object_or_404(User, id=id)
        try:
            Subscriptions.objects.get(
                author=author, subscriber=request.user).delete()
        except ObjectDoesNotExist:
            data = {'message': 'Вы не подписаны на этого пользователя'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
