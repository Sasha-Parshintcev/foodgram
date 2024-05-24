import datetime as dt

from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Follow, User
from users.validators import username_validator


# class UserSerializer(serializers.ModelSerializer):
#     """Сериализатор для запросов к переопределенной модели User."""
#     class Meta:
#         model = User
#         fields = (
#             'username', 'email', 'first_name',
#             'last_name'
#         )
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=User.objects.all(),
#                 fields=('username', 'email'),
#                 message='Такие username, email уже есть!',
#             )
#         ]