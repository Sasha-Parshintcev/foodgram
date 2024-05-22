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


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Recipe."""
    
    ingredients = IngredientSerializer()
    tags = TagSerializer()

    class Meta:
        model = Recipe
        fields = (
            'author', 'name', 'image', 'description',
            'ingredients', 'tags', 'cooking_time', 'pub_date'
        )
