# import datetime as dt

# from django.core.exceptions import ValidationError
# from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator

# from food.models import Tag, Ingredient, Recipe, RecipeIngredient, Follow, User
# from users.validators import username_validator


# class TagSerializer(serializers.ModelSerializer):
#     """Сериализатор для запросов к Tag."""

#     class Meta:
#         model = Tag
#         fields = ('id', 'name', 'slug')


# class IngredientSerializer(serializers.ModelSerializer):
#     """Сериализатор для запросов к Ingredient."""

#     class Meta:
#         model = Ingredient
#         fields = ('id', 'name', 'measurement_unit')


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


# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     """Сериализатор для запросов к RecipeIngredient."""

#     ingredients = IngredientSerializer() #many=True
#     recipe = RecipeSerializer() #many=True

#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'ingredients', 'recipe', 'amount')


# # class FollowSerializer(serializers.ModelSerializer):
# #     """Сериализатор подписок."""
# #     user = serializers.SlugRelatedField(
# #         read_only=True,
# #         slug_field='username',
# #         default=serializers.CurrentUserDefault()
# #     )
# #     following = serializers.SlugRelatedField(
# #         slug_field='username',
# #         queryset=User.objects.all()
# #     )

# #     def validate(self, data):
# #         """Проверка создание подписки на самого себя и на дубликат подписки."""
# #         follower = self.context['request'].user
# #         following = data.get('following')

# #         if follower == following:
# #             raise serializers.ValidationError(
# #                 'Нельзя создать подписку на самого себя.'
# #             )

# #         if Follow.objects.filter(user=follower, following=following).exists():
# #             raise serializers.ValidationError(
# #                 'Подписка на данного пользователя уже существует.'
# #             )

# #         return data

# #     class Meta:
# #         model = Follow
# #         fields = ('user', 'following',)


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


