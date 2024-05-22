from django.shortcuts import render

from food.models import Tag, Ingredient, Recipe, RecipeIngredient
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeIngredientSerializer,
)

class TagViewSet(ListCreateDestroyViewSet):
    """ViewSet для работы с тегами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes
    # lookup_field = 'slug'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)
