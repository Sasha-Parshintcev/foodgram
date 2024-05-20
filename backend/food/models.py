from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        'Название рецепта',
        help_text='Например "Крабовый салат"',
        max_length=16
    )
    image = models.ImageField(
        'Изображение',
        help_text='Загрузите изображение для вашего рецепта',
        upload_to='images/',
        null=True,
        default=None
    )
    description = models.TextField(
        'Описание',
        help_text='Описание и инструкция по приготовлению блюда'
    )
    Ingredients = models.ManyToManyField(
        'Ингредиенты',
        help_text='Продукты для приготовления блюда по рецепту'
        Ingredient,
        through='IngredientRecipe'
    )
    tag = models.ManyToManyField(
        'Тег',
        help_text='Можно установить несколько тегов на один рецепт'
        Tag,
        related_name='recipes'
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        help_text='Время приготовления (в минутах), целое число',
        validators=[
            MinValueValidator(
                1,
                'Время приготовления не может быть меньше 1 минуты',
            )
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )        

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}\n{self.text}'