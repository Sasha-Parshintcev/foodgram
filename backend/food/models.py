from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()


TEXT_LENGTH_LIMIT=20
MIN_COOK_TIME=1


class Tag(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        'Название',
        max_length=32,
        unique=True
        
    )
    slug = models.SlugField(
        'Идентификатор',
        max_length=32,
        # regex=r'^[\w.@+-]+$',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:TEXT_LENGTH_LIMIT]


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
        upload_to='recipes/',
        null=True,
        default=None
    )
    text = models.TextField(
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
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        null=False,
        verbose_name='Время приготовления',
        help_text='Введите время приготовления',
        validators=(
            MinValueValidator(
                MIN_COOK_TIME,
                f'Минимальное время: {MIN_COOK_TIME} минута'
            ),
        )
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
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredient_in_recipe',
        verbose_name='Рецепты',
        on_delete=models.CASCADE
    )
    ingredients = models.ForeignKey(
        Ingredient,
        related_name='ingredients_list',
        verbose_name='Ингредиенты',
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        help_text='Требуемое количество для рецепта (целое число)'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('ingredients', 'recipe'),
                name='unique_ingredient'
            ),
        )
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


# class Favorites(models.Model):
