from django.shortcuts import render

from food.models import Tag, Ingredient, Recipe
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer
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


