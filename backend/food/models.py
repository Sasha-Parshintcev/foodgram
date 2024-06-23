from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
import base64

User = get_user_model()


# MAX_LENGTH_SHORT_LINK=200
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
        max_length=128,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        help_text='Применяйте наиболее подходящую единицу измерения',
        max_length=64 ,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
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
        through='RecipeIngredient',
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
        # null=False,
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
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}\n{self.text[:TEXT_LENGTH_LIMIT]}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_favorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name} в избраннное'

class RecipeIngredient(models.Model):
    """Модель ингредиентов для рецепта."""
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredient_in_recipe',
        verbose_name='Рецепты',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_in_ingredient',
        verbose_name='Ингредиенты',
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        help_text='Требуемое количество для рецепта (целое число)'
    )

    class Meta:
        # constraints = (
        #     models.UniqueConstraint(
        #         fields=('ingredient', 'recipe'),
        #         name='unique_ingredient'
        #     ),
        # )
        # default_related_name = 'ingredient_in_recipe'
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_cart'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return (f'{self.user.username} добавил'
                f'{self.recipe.name} в список покупок')
    

# class Shortener(models.Model):
#     '''
#     Модель короткой ссылки.
#     ''' 
#     create = models.DateTimeField(auto_now_add=True)
#     short_url = models.CharField(max_length=15, unique=True, blank=True)

#     class Meta:
#         ordering = ["-create"]

#     def __str__(self):
#         return f'{self.short_url}'