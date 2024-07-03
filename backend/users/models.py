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
        validators = [UnicodeUsernameValidator()],
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким username уже существует.',
        }
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
    avatar = models.ImageField(
        upload_to='users/',
        blank=True,
        default=None
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:TEXT_LENGTH_LIMIT]


class Subscription(models.Model):
    """Модель подписок пользователя."""
    user = models.ForeignKey(
        User,
        null = True,
        unique=True,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь')
    author = models.ForeignKey(
        User,
        null = True,
        unique=True,
        verbose_name='Подписка',
        related_name='following',
        on_delete=models.CASCADE,
        help_text='Подписаться на автора рецепта')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_following')
        ]

    def __str__(self):
        return (f'{self.user[:TEXT_LENGTH_LIMIT]}'
                f'подписался на {self.author[:TEXT_LENGTH_LIMIT]}')
