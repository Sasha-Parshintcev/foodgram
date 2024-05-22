import datetime as dt

# from django.core.exceptions import ValidationError
from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator

from food.models import Tag, Ingredient, Recipe, RecipeIngredient


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Tag."""

    class Meta:
        model = Tag
        fields = ('name', 'slug')


