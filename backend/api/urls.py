from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, TagViewSet, IngredientViewSet, RecipeViewSet, SubscriptionViewSet



api_v1 = DefaultRouter()
api_v1.register('users', UserViewSet, basename='users')
api_v1.register('tags', TagViewSet, basename='tags')
api_v1.register('ingredients', IngredientViewSet, basename='ingredients')
api_v1.register('recipes', RecipeViewSet, basename='recipes')
api_v1.register(
    'users/(?P<id>[^/.]+)/subscribe',
    SubscriptionViewSet, basename='subscribe'
)

urlpatterns = [
    path('', include(api_v1.urls)),
    re_path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    # path('auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.authtoken')),
    # re_path(r'^auth/token/(login|logout)/', TokenUserAuth.as_view()),
    # *api_v1.urls
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
