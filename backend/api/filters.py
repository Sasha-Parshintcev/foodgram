from django_filters.rest_framework import FilterSet, filters

from food.models import Recipe, Tag
from users.models import User


class RecipeFilter(FilterSet):
    """Фильтр выборки рецептов по определенным полям."""
    author = filters.ModelMultipleChoiceFilter(
        field_name='author__id',
        to_field_name='id',
        queryset=User.objects.all()
    )

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )

    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, queryset, name, value):
        """
        Фильтрует queryset, чтобы включать только объекты,
        добавленные в избранное текущим пользователем.
        """
        if value:
            return queryset.filter(
                favorites__user=self.request.user.id
            )
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрует queryset, чтобы включать только объекты,
        добавленные в корзину текущим пользователем.
        """
        if value:
            return queryset.filter(
                cart__user=self.request.user.id
            )
        return queryset
