# from rest_framework import serializers

# from .models import User


# class UserSerializer(serializers.ModelSerializer):
#     """Сериализатор пользователя."""
#     # is_subscribed = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name',
#                   'last_name')
        # extra_kwargs = {'password': {'write_only': True},
        #                 'is_subscribed': {'read_only': True}}

    # def create(self, validated_data):
    #     """
    #     Функция create создает нового пользователя
    #     и генерирует токен авторизации для него.
    #     """
    #     user = User.objects.create_user(**validated_data)
    #     Token.objects.create(user=user)
    #     return user
