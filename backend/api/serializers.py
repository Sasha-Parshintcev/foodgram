from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserSerializer
import base64
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import User, Subscription
from food.models import (
    Tag, Ingredient, Recipe, Favorite,
    ShoppingCart, RecipeIngredient
)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с избранными рецептами."""
    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        """
        Преобразует объект модели в представление,
        используя сериализатор рецепта.
        """
        request = self.context.get('request')
        return RecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Ingredient."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к RecipeIngredient."""
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )

    
class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    '''Сериализатор для модели RecipeIngredient.'''
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Tag."""
    
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug'
        )

class Base64ImageField(serializers.ImageField):
    """
    Пользовательское поле сериализатора Django REST Framework,
    которое обрабатывает данные изображения в кодировке Base64.

    Это поле позволяет клиенту отправлять данные изображения в виде строки
    в кодировке Base64 в полезных данных запроса.
    Затем поле декодирует строку и создаст объект ContentFile,
    который можно сохранить в базе данных.

    Поле ожидает, что данные изображения будут
    в формате `data:image/png;base64,<base64_data>`.
    """
    def to_internal_value(self, data):
        """
        Переопределяет метод to_internal_value() по умолчанию
        для обработки данных изображения в кодировке Base64.
        """
        if isinstance(data, str) and data.startswith('data:image/png'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)

class UserSerializer(UserSerializer):
    """Сериализатор пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(required=False, allow_null=True, read_only=True)
    extra_kwargs = {'password': {'write_only': True},
                        'is_subscribed': {'read_only': True}}

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )
    
    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на указанный объект."""
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False

    def create(self, validated_data):
        """Создает нового пользователя с указанными данными."""
        return User.objects.create_user(**validated_data)


class RecipeShortSerializer(serializers.ModelSerializer):
        """Сериализатор для показа сокращенной информации о рецепте."""

        class Meta:
            model = Recipe
            fields = (
                'id',
                'name',
                'image',
                'cooking_time'
            )

class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для работы со списком покупок."""
    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]

    def to_representation(self, instance):
        """
        Метод для преобразования объекта модели
        в сериализованное представление.
        """
        request = self.context.get('request')
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': request}
        ).data

class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Recipe."""
    ingredients = RecipeIngredientSerializer(
        source='ingredient_in_recipe',
        many=True
    )
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        """
        Проверяет, добавлен ли переданный объект obj
        в список избранного текущим пользователем.
        """
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет, добавлен ли переданный объект obj
        в корзину покупок текущего пользователя.
        """
        request = self.context.get('request')
        if request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добаления/обновления рецепта."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    image = Base64ImageField()
    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def create_ingredients(self, recipe, ingredients):
        """Вспомогательная функция для добавления ингредиентов.
        Используется при создании/редактировании рецепта."""
        RecipeIngredient.objects.bulk_create(
                [
                    RecipeIngredient(
                        recipe=recipe,
                        ingredient=ingredient['id'],
                        amount=ingredient['amount']
                    ) for ingredient in ingredients
                ]
            )

    @transaction.atomic
    def create(self, validated_data):
        """Создает новый рецепт в базе данных."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет существующий рецепт в базе данных."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(instance, ingredients)
        return instance
    
    def to_representation(self, instance):
        """
        Метод для преобразования объекта модели
        в сериализованное представление.
        """
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def validate(self, data):
        """
        Валидация на количество ингредиентов в рецепте и выбрасывание
        исключения в случае повторения тегов или ингредиентов.
        """
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                'Забыли добавить ингредиенты в рецепт'
            )
        ingredients_list = []
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Поле ингредиентов не может быть пустым'
            )

        for ingredient in ingredients:
            if ingredient.get('amount') <= 0:
                raise serializers.ValidationError(
                    'Количество не может быть меньше 1'
                )
            
            ingredient_id = ingredient.get('id')
            if not ingredient_id:
                raise serializers.ValidationError(
                    'Поле "id" ингредиента не может быть пустым'
                )
            
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    'Вы пытаетесь добавить в рецепт два одинаковых ингредиента'
                )
            
            ingredients_list.append(ingredient_id)
        
        tags = data.get('tags', [])
        if not tags:
            raise serializers.ValidationError(
                'Поле тегов не может быть пустым.'
            )
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                'Рецепт не может содержать повторяющиеся теги'
            )
        
        return data


class AvatarSerializer(serializers.Serializer):
    """Сериализатор аватара."""
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        fields = ('avatar',)

    
class SubscriptionSerializer(serializers.ModelSerializer):
    """Просмотр списка подписок пользователя."""

    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = RecipeShortSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на переданный объект."""
        request = self.context.get('request')
        user = self.context['request'].user
        if not request or not user.is_authenticated:
            return False
        return obj.following.filter(user=user).exists()

    
class SubscribeSerializer(serializers.Serializer):
    """Сериаоизатор добавления и удаления подписок пользователя."""

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def validate(self, data):
        """Валидация на повторную подписку или на себя."""
        user = self.context.get('request').user
        author = get_object_or_404(User, pk=self.context['id'])
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя'
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя'
            )
        return data

    def create(self, validated_data):
        """Создает новую подписку в базе данных."""
        user = self.context.get('request').user
        author = get_object_or_404(User, pk=validated_data['id'])
        Subscription.objects.create(user=user, author=author)
        serializer = SubscriptionSerializer(
            author, context={'request': self.context.get('request')}
        )
        return serializer.data
