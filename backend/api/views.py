from django.shortcuts import render
from rest_framework import filters, status, viewsets, mixins

from food.models import Tag, Ingredient, Recipe, RecipeIngredient, Follow
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    # RecipeIngredientSerializer,
    FollowSerializer
)

class TagViewSet(ListCreateDestroyViewSet):
    """ViewSet для работы с тегами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes
    # lookup_field = 'slug'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)


class IngredientViewSet(ListCreateDestroyViewSet):
    """ViewSet для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes
    # lookup_field = 'slug'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)


class RecipeViewSet(ListCreateDestroyViewSet):
    """ViewSet для работы с рецептом."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # permission_classes
    # lookup_field = 'slug'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)


class FollowViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет фолловера."""
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    # permission_classes = (permissions.IsAuthenticated,)
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('user__username', 'following__username',)

    def get_queryset(self):
        """Получение подписок."""
        return get_object_or_404(User, username=self.request.user).follower

    def perform_create(self, serializer):
        """Сохраняет объект, указывая пользователя."""
        serializer.save(user=self.request.user)


# class RecipeIngredientViewSet(ListCreateDestroyViewSet):
#     """ViewSet для работы с ингредиентами."""
#     queryset = RecipeIngredient.objects.all()
#     serializer_class = RecipeIngredientSerializer
    # permission_classes
    # lookup_field = 'slug'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)
