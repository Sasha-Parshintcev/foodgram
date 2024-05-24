from django.db import models
from django.contrib.auth.models import AbstractUser


# class User(AbstractUser):
#     email = models.EmailField(
#         unique=True,
#         max_length=254,
#         verbose_name='email',
#         help_text='Введите адрес электронной почты'
#     )

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

#     class Meta:
#         verbose_name = 'Пользователь'
#         verbose_name_plural = 'Пользователи'

#     def __str__(self):
#         return self.username


# class Follow(models.Model):
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

