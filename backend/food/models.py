from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='food',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        'Название',
        max_length=16
    )
    image = models.ImageField(
        'Изображение',
        upload_to='food/',
        null=True,
        default=None
    )
    description = models.TextField(
        'Описание'
    )
    Ingredients = models.ManyToManyField(
        'Ингредиенты',
        Ingredient,
        through='IngredientRecipe'
    )
    # Ингредиенты — продукты для приготовления блюда по рецепту. Множественное поле с выбором из предустановленного списка и с указанием количества и единицы измерения.
    tag = models.ManyToManyField(
        'Тег',
        Tag,
        through='TagRecipe'
    )
    # Тег. Можно установить несколько тегов на один рецепт.
    Время приготовления в минутах.
        

    def __str__(self):
        return self.name