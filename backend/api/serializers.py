import datetime as dt

# from django.core.exceptions import ValidationError
from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator

from food.models import Tag, Ingredient, Recipe, RecipeIngredient


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Recipe."""
    
    ingredient = IngredientSerializer() #many=True
    tags = TagSerializer() #many=True

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'description',
            'ingredient', 'tags', 'cooking_time', 'pub_date'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к RecipeIngredient."""

    ingredient = IngredientSerializer() #many=True
    recipe = RecipeSerializer() #many=True

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'ingredient', 'recipe', 'amount')