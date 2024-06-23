from django.utils.translation import gettext_lazy as _
# from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from djoser.serializers import UserSerializer
import base64
from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.response import Response
# import api.serializers

# from .utils import create_ingredients
from users.models import User, Subscription
from food.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart, RecipeIngredient
#, RecipeLink

class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с избранными рецептами."""
    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Ingredient."""
    # id = serializers.PrimaryKeyRelatedField(read_only=True)
    # amount = serializers.CharField(source='ingredient.amount', required=True) #
    # id = serializers.IntegerField(source='ingredient.id', read_only=True)
    # name = serializers.CharField(source='ingredient.name', read_only=True)
    # measurement_unit = serializers.CharField(
    #     source='ingredient.measurement_unit',
    #     read_only=True
    # )

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


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
    # id = serializers.ReadOnlyField(source='ingredient.id') #
    # name = serializers.ReadOnlyField() # source='ingredient.name', read_only=True
    # measurement_unit = serializers.ReadOnlyField() #,read_only=True source='ingredient.measurement_unit'
    # id = serializers.ReadOnlyField(source='ingredient.id')
    # name = serializers.CharField(source='ingredient.name')
    # measurement_unit = serializers.CharField(
    #     source='ingredient.measurement_unit')
    # amount = serializers.CharField(required=True) #source='amount', 
    # id = serializers.IntegerField(read_only=True)
    # name = serializers.CharField(read_only=True)
    # measurement_unit = serializers.CharField(required=True)
    
    
    # ingredients = IngredientSerializer() #many=True
    # recipe = RecipeSerializer() #many=True

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
    # validators = [
    #         UniqueTogetherValidator(
    #             queryset=RecipeIngredient.objects.all(),
    #             fields=['ingredient', 'recipe']
    #         )
    #     ]
    
class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для модели RecipeIngredient.
    '''
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
        # source='ingredient'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )

    
class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Tag."""
    # id = serializers.IntegerField(source='tag.id', read_only=True)
    # name = serializers.CharField(source='ta.name', read_only=True)
    # slug = serializers.RegexField(
    #     regex=r'^[\w.@+-]+$') #, required=False
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


# class TagListSerializer(serializers.ModelSerializer):
#     """Сериализатор для запросов к Tag."""
#     tags = TagSerializer(many=True)

#     class Meta:
#         model = Tag
#         fields = ('tags',)
    

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
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
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar',)
    
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RecipeShortSerializer(serializers.ModelSerializer):
        """Сериализатор для показа короткой информации о рецепте."""

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
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': request}
        ).data

class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Recipe."""
    
    # ingredients = RecipeIngredientSerializer(many=True, read_only=False) #, required=False, source='ingredient_in_recipe'
    # tags = TagSerializer(many=True, read_only=False) #, required=False, source='recipes'
    # ingredients = RecipeIngredientSerializer(many=True, read_only=False, source='ingredient_in_recipe')
    # ingredients = RecipeIngredientSerializer(source='ingredient_in_recipe', many=True)
    ingredients = RecipeIngredientSerializer(source='ingredient_in_recipe', many=True)
    # ingredients = serializers.SerializerMethodField(read_only=True) #many=True, 
    tags = TagSerializer(many=True, read_only=True)
    # image = Base64ImageField()  #required=False
    author = UserSerializer(read_only=True) #required=False,      source='author.username'
    is_favorited = serializers.SerializerMethodField(
        read_only=True,
        # default=False
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True,
        # default=False
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart','name', 'image', 'text',
            'cooking_time',
        )
        #  
    
    # def get_id(self, obj):
    #     return f'{obj.pk}'

    # def get_ingredients(self, obj):
    #     recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
    #     return [
    #         {
    #             'id': recipe_ingredient.ingredient.id,
    #             'name': recipe_ingredient.ingredient.name,
    #             'amount': recipe_ingredient.amount,
    #             'measurement_unit':
    #             recipe_ingredient.ingredient.measurement_unit,
    #         }
    #         for recipe_ingredient in recipe_ingredients
    #     ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        return False
    # def get_ingredients(self, obj):
    #     recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)

    #     return [
    #         {
    #             'id': recipe_ingredient.ingredient.id,
    #             'name': recipe_ingredient.ingredient.name,
    #             'amount': recipe_ingredient.amount,
    #             'measurement_unit':
    #                 recipe_ingredient.ingredient.measurement_unit
    #         }
    #         for recipe_ingredient in recipe_ingredients
    #     ]
    
    # def get_is_favorited(self, obj):
    #     request = self.context.get('request')
    #     return (request and request.user.is_authenticated
    #             and Favorite.objects.filter(
    #                 user=request.user, recipe=obj
    #             ).exists())

    # def get_is_in_shopping_cart(self, obj):
    #     request = self.context.get('request')
    #     return (request and request.user.is_authenticated
    #             and ShoppingCart.objects.filter(
    #                 user=request.user, recipe=obj
    #             ).exists())
    


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добаления/обновления рецепта."""
    # author = UserSerializer(required=False, read_only=True)
    author = serializers.SlugRelatedField(read_only=True, slug_field='username')
    image = Base64ImageField()
    ingredients = RecipeIngredientWriteSerializer(many=True) #, allow_empty=False   source='ingredient_in_recipe'
    # ingredients = serializers.ListField(
    #     child=serializers.DictField(),
    #     # write_only=True,
    #     # required=True,
    #     # allow_empty=False,
    # )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        # allow_empty=False
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
            'cooking_time',
        )

    # @staticmethod
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
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновление рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(instance, ingredients)
        return instance
    
    def to_representation(self, instance):
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
            raise serializers.ValidationError('Забыли добавить ингредиенты в рецепт')
        ingredients_list = []
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError('Поле ингредиентов не может быть пустым')

        for ingredient in ingredients:
            if ingredient.get('amount') <= 0:
                raise serializers.ValidationError('Количество не может быть меньше 1')
            
            ingredient_id = ingredient.get('id')
            if not ingredient_id:
                raise serializers.ValidationError('Поле "id" ингредиента не может быть пустым')
            
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError('Вы пытаетесь добавить в рецепт два одинаковых ингредиента')
            
            ingredients_list.append(ingredient_id)
        
        tags = data.get('tags', [])
        if not tags:
            raise serializers.ValidationError('Поле тегов не может быть пустым.')
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError('Рецепт не может содержать повторяющиеся теги')
        
        return data

    # def get_is_favorited(self, obj):
    #     request = self.context.get('request')
    #     return (request and request.user.is_authenticated
    #             and Favorite.objects.filter(
    #                 user=request.user, recipe=obj
    #             ).exists())

    # def get_is_in_shopping_cart(self, obj):
    #     request = self.context.get('request')
    #     return (request and request.user.is_authenticated
    #             and ShoppingCart.objects.filter(
    #                 user=request.user, recipe=obj
    #             ).exists())

# class RecipeLinkSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RecipeLink
#         fields = ('original_url', 'short_url',)




class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        fields = ('avatar',)

        # def get_avatar(self, obj):
    #     if obj.avatar:
    #         return {'avatar': user.avatar.url}'
    #     return None

    # def validate_avatar(self, value):
    #     if value.size > 1024 * 1024:
    #         raise serializers.ValidationError("Максимальный размер аватара 1MB.")
    #     return value
    
# class AvatarSerializer(serializers.Serializer):
#        avatar = serializers.ImageField()
   
#        def update(self, instance, validated_data):
#            instance.profile.avatar = validated_data.get('avatar', instance.profile.avatar)
#            instance.save()
#            return instance
       
#        def destroy(self, instance):
#            instance.profile.avatar = None
#            instance.profile.save()
#            return instance
       
#        class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name',
#                   'last_name', 'is_subscribed', 'avatar',)
    
class SubscriptionSerializer(serializers.ModelSerializer):
    """Просмотр списка подписок пользователя."""

    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = RecipeShortSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = self.context['request'].user
        if not request or not user.is_authenticated:
            return False
        return obj.following.filter(user=user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit_recipes = request.query_params.get('recipes_limit')
        if limit_recipes is not None:
            recipes = obj.recipes.all()[:(int(limit_recipes))]
        else:
            recipes = obj.recipes.all()
        context = {'request': request}
        return RecipeShortSerializer(recipes, many=True,
                                     context=context).data
    
class SubscribeSerializer(serializers.Serializer):
    """Добавление и удаление подписок пользователя."""

    def validate(self, data):
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
        user = self.context.get('request').user
        author = get_object_or_404(User, pk=validated_data['id'])
        Subscription.objects.create(user=user, author=author)
        serializer = SubscriptionSerializer(
            author, context={'request': self.context.get('request')}
        )
        return serializer.data
    
# class SubscriptionSerializer(serializers.ModelSerializer):
#     """Сериализатор подписки."""
#     email = serializers.ReadOnlyField(source='author.email')
#     id = serializers.ReadOnlyField(source='author.id')
#     username = serializers.ReadOnlyField(source='author.username')
#     first_name = serializers.ReadOnlyField(source='author.first_name')
#     last_name = serializers.ReadOnlyField(source='author.last_name')
#     is_subscribed = serializers.SerializerMethodField()
#     recipes = serializers.SerializerMethodField()
#     recipes_count = serializers.SerializerMethodField()

#     class Meta:
#         model = Subscription
#         fields = ('email', 'id', 'username', 'first_name',
#                   'last_name', 'is_subscribed', 'recipes', 'recipes_count')

#     def get_is_subscribed(self, obj):
#         user = self.context.get('request').user
#         if not user.is_anonymous:
#             return Subscription.objects.filter(
#                 user=obj.user,
#                 author=obj.author).exists()
#         return False

    # def get_recipes(self, obj):
    #     request = self.context.get('request')
    #     limit = request.GET.get('recipes_limit')
    #     recipes = Recipe.objects.filter(author=obj.author)
    #     if limit and limit.isdigit():
    #         recipes = recipes[:int(limit)]
    #     return api.serializers.RecipeMiniSerializer(recipes, many=True).data

    # def get_recipes_count(self, obj):
    #     return Recipe.objects.filter(author=obj.author).count()

    def validate(self, data):
        author = self.context.get('author')
        user = self.context.get('request').user
        if Subscription.objects.filter(
                author=author,
                user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST)
        if user == author:
            raise ValidationError(
                detail='Невозможно подписаться на себя!',
                code=status.HTTP_400_BAD_REQUEST)
        return data

# class SubscriptionSerializer(serializers.ModelSerializer):
#     """Сериализатор подписок."""
#     user = serializers.SlugRelatedField(
#         read_only=True,
#         slug_field='username',
#         default=serializers.CurrentUserDefault()
#     )
#     subscribing = serializers.SlugRelatedField(
#         slug_field='username',
#         queryset=User.objects.all()
#     )

#     def validate(self, data):
#         """Проверка создание подписки на самого себя и на дубликат подписки."""
#         subscriber = self.context['request'].user
#         subscribing = data.get('subscribing')

#         if subscriber == subscribing:
#             raise serializers.ValidationError(
#                 'Нельзя создать подписку на самого себя.'
#             )

#         if Subscription.objects.filter(user=subscriber, following=subscribing).exists():
#             raise serializers.ValidationError(
#                 'Подписка на данного пользователя уже существует.'
#             )

#         return data

#     class Meta:
#         model = Subscription
#         fields = ('user', 'subscribing',)











# class AuthTokenSerializer(serializers.Serializer):
#     email = serializers.CharField(
#         label=_('email'),
#         write_only=True
#     )
#     password = serializers.CharField(
#         label=_('password'),
#         style={'input_type': 'password'},
#         trim_whitespace=False,
#         write_only=True
#     )
#     token = serializers.CharField(
#         label=_("Token"),
#         read_only=True
#     )

#     def update(self, instance, validated_data):
#         raise NotImplementedError('Нельзя использовать для обновления')

#     def create(self, validated_data):
#         raise NotImplementedError('Нельзя использовать для создания')

#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')

#         if email and password:
#             user = authenticate(request=self.context.get('request'),
#                                 email=email, password=password)

#             if not user:
#                 msg = _('Unable to log in with provided credentials.')
#                 raise serializers.ValidationError(msg, code='authorization')
#         else:
#             msg = _('Must include "username" and "password".')
#             raise serializers.ValidationError(msg, code='authorization')

#         attrs['user'] = user
#         return attrs
    

# class PasswordSerializer(serializers.Serializer):
#     def update(self, instance, validated_data):
#         raise NotImplementedError('Нельзя использовать для обновления')

#     def create(self, validated_data):
#         raise NotImplementedError('Нельзя использовать для создания')

#     def validate(self, attrs):
#         new_password = attrs['new_password']
#         current_password = attrs['current_password']
#         if self.instance.check_password(current_password):
#             return dict(password=new_password)
#         raise serializers.ValidationError(
#             dict(current_password='Некорректное значение.')
#         )

#     new_password = serializers.CharField(required=True)
#     current_password = serializers.CharField(required=True)

# import datetime as dt

# from django.core.exceptions import ValidationError
# from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator

# from food.models import Tag, Ingredient, Recipe, RecipeIngredient, Follow
# from users.validators import username_validator


# class TagSerializer(serializers.ModelSerializer):
#     """Сериализатор для запросов к Tag."""

#     class Meta:
#         model = Tag
#         fields = ('id', 'name', 'slug')


# 


# class RecipeSerializer(serializers.ModelSerializer):
#     """Сериализатор для запросов к Recipe."""
    
#     ingredients = IngredientSerializer() #many=True
#     tags = TagSerializer() #many=True

#     class Meta:
#         model = Recipe
#         fields = (
#             'id', 'author', 'name', 'image', 'description',
#             'ingredients', 'tags', 'cooking_time', 'pub_date'
#         )
    # @transaction.atomic
    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     ingredients = validated_data.pop('recipeingredients')
    #     tags = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(author=request.user, **validated_data)
    #     recipe.tags.set(tags)
    #     create_ingredients(ingredients, recipe)
    #     return recipe

    # @transaction.atomic
    # def update(self, instance, validated_data):
    #     ingredients = validated_data.pop('recipeingredients')
    #     tags = validated_data.pop('tags')
    #     instance.tags.clear()
    #     instance.tags.set(tags)
    #     RecipeIngredient.objects.filter(recipe=instance).delete()
    #     super().update(instance, validated_data)
    #     create_ingredients(ingredients, instance)
    #     instance.save()
    #     return instance

# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     """Сериализатор для запросов к RecipeIngredient."""

#     ingredients = IngredientSerializer() #many=True
#     recipe = RecipeSerializer() #many=True

#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'ingredients', 'recipe', 'amount')


# # 


# # class RegistrationSerializer(serializers.ModelSerializer):
# #     """Сериализатор для регистрации новых пользоватлелей и
# #     получения письма с кодом подтверждения."""
# #     username = serializers.RegexField(
# #         regex=r'^[\w.@+-]+$', max_length=150, required=True)
# #     email = serializers.EmailField(max_length=254)

# #     class Meta:
# #         model = User
# #         fields = ('username', 'email')

#     # def username_validator(self, value):
#     # forbidden_name = 'me'
#     # if value == forbidden_name:
#     #     raise ValidationError(
#     #         'Использовать "me" в качестве username запрещено.')

#     # def validate(self, data):
#     #     username = data['username']
#     #     email = data['email']
#     #     user_with_data_email = User.objects.filter(
#     #         email=email).first()
#     #     user_with_data_username = User.objects.filter(
#     #         username=username).first()
#     #     if user_with_data_email:
#     #         if getattr(user_with_data_email, "username") != username:
#     #             raise ValidationError('Такой email занят.')
#     #     if user_with_data_username:
#     #         if getattr(user_with_data_username, "email") != email:
#     #             raise ValidationError('Такой username занят.')
#     #     return data


# # class TokenSerializer(serializers.ModelSerializer):
# #     """Сериализатор для получения токена."""
# #     confirmation_code = serializers.CharField()

# #     class Meta:
# #         model = User
# #         fields = ('username', 'confirmation_code')


