from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet


api_v1 = DefaultRouter()
api_v1.register('users', UserViewSet, basename='users')
# api_v1.register(
#     'users/(?P<id>[^/.]+)/subscribe',
#     FollowViewSet, basename='subscribe'
# )

urlpatterns = [
    path('', include(api_v1.urls)),
    # path('api-token-auth/', views.obtain_auth_token),
    # path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]


# from django.urls import include, path
# from rest_framework.routers import DefaultRouter

# from .views import (
#     TagViewSet,
#     IngredientViewSet,
#     RecipeViewSet,
#     FollowViewSet,
#     UserViewSet
#     # RecipeIngredientViewSet
# )


# router_v1 = DefaultRouter()
# router_v1.register('tags', TagViewSet, basename='tags')
# router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
# router_v1.register('recipes', RecipeViewSet, basename='recipes')
# router_v1.register('users', UserViewSet, basename='users')
# router_v1.register(
#     'users/(?P<id>[^/.]+)/subscribe',
#     FollowViewSet, basename='subscribe'
# )
