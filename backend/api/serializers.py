from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.db import transaction
import base64
from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import ValidationError
import api.serializers

from users.models import User, Subscription
from food.models import Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
    
class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов к Tag."""
    slug = serializers.RegexField(
        regex=r'^[\w.@+-]+$', required=True)
    
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


class UserSerializer(serializers.ModelSerializer):
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
    """Сериализатор подписки."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscription.objects.filter(
                user=obj.user,
                author=obj.author).exists()
        return False

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


