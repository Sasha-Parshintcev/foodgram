from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()


TEXT_LENGTH_LIMIT=10


class Tag(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        'Название',
        max_length=20,
        unique=True
        
    )
    slug = models.SlugField(
        'Идентификатор',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        verbose_name='Название ингредиента',
        help_text='Названия ингридинтов для блюда',
        max_length=256,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        help_text='Применяйте наиболее подходящую единицу измерения',
        max_length=15,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='Уникальная запись ингредиент - единица измерения',
            )
        ]

    def __str__(self):
        return self.name[:TEXT_LENGTH_LIMIT]


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
        max_length=256
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
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        help_text='Продукты для приготовления блюда по рецепту',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        help_text='Можно установить несколько тегов на один рецепт',
        verbose_name='Теги',
        blank=True,
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
        return f'{self.name}\n{self.text[:TEXT_LENGTH_LIMIT]}'


class RecipeIngredient(models.Model):
    """Модель ингредиентов для рецепта."""
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        help_text='Выберите ингредиент',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        help_text='Требуемое количество для рецепта (целое число)',
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return self.ingredient.name[:TEXT_LENGTH_LIMIT]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь')
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'following'],
                                    name='user_following')
        ]

    def __str__(self):
        return (f'{self.user[:TEXT_LENGTH_LIMIT]}'
                f'подписался на {self.following[:TEXT_LENGTH_LIMIT]}')
