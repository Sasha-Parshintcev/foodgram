from django.shortcuts import render
from rest_framework import filters, status, viewsets

from food.models import Tag, Ingredient, Recipe, RecipeIngredient
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeIngredientSerializer
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


class RecipeIngredientViewSet(ListCreateDestroyViewSet):
    """ViewSet для работы с ингредиентами."""
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
    # permission_classes
    # lookup_field = 'slug'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)