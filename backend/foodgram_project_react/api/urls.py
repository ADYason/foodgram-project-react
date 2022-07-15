from django.urls import include, path
from djoser.urls.authtoken import views
from rest_framework import routers

from .views import (FavoriteViewSet, IngredientsViewSet, RecipeViewSet,
                    ShoppingCartViewSet, SubscriptionViewSet,
                    TagListRetriveViewSet, UserCreateRetriveViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserCreateRetriveViewSet)
router_v1.register('tags', TagListRetriveViewSet)
router_v1.register('recipes', RecipeViewSet)
router_v1.register(r'recipes/(?P<id>\d+)/shopping_cart', ShoppingCartViewSet)
router_v1.register(r'recipes/(?P<id>\d+)/favorite', FavoriteViewSet)
router_v1.register(r'users/(?P<id>\d+)/subscribe', SubscriptionViewSet)
router_v1.register('ingredients', IngredientsViewSet)


urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/token/login/', views.TokenCreateView.as_view(), name='signin'),
    path(
        'auth/token/logout/',
        views.TokenDestroyView.as_view(),
        name='logout'
    ),
]
