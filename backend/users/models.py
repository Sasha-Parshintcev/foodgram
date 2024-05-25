from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


TEXT_LENGTH_LIMIT=20


class User(AbstractUser):
    """
    Модель пользователя.
    Регистрация с помощью email.
    """
    email = models.EmailField(
        'email-адрес',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        'Логин',
        max_length=150,
        validators = [UnicodeUsernameValidator()]
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:TEXT_LENGTH_LIMIT]


# class Follow(models.Model):
#     """Модель подписок пользователя."""
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='follower',
#         verbose_name='Пользователь')
#     following = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='following',
#         verbose_name='Автор')

#     class Meta:
#         verbose_name = 'Подписка'
#         verbose_name_plural = 'Подписки'
#         constraints = [
#             models.UniqueConstraint(fields=['user', 'following'],
#                                     name='user_following')
#         ]

#     def __str__(self):
#         return (f'{self.user[:TEXT_LENGTH_LIMIT]}'
#                 f'подписался на {self.following[:TEXT_LENGTH_LIMIT]}')

