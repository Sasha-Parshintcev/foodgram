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
    
    ingredients = IngredientSerializer() #many=True
    tags = TagSerializer() #many=True

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'description',
            'ingredients', 'tags', 'cooking_time', 'pub_date'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к RecipeIngredient."""

    ingredients = IngredientSerializer() #many=True
    recipe = RecipeSerializer() #many=True

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'ingredients', 'recipe', 'amount')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    def validate(self, data):
        """Проверка создание подписки на самого себя и на дубликат подписки."""
        follower = self.context['request'].user
        following = data.get('following')

        if follower == following:
            raise serializers.ValidationError(
                'Нельзя создать подписку на самого себя.'
            )

        if Follow.objects.filter(user=follower, following=following).exists():
            raise serializers.ValidationError(
                'Подписка на данного пользователя уже существует.'
            )

        return data

    class Meta:
        model = Follow
        fields = ('user', 'following',)