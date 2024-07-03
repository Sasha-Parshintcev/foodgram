from rest_framework import status
from rest_framework.response import Response
from django.db.models import Sum

from food.models import Ingredient, RecipeIngredient


def create_model_instance(request, instance, serializer_name):
    """Вспомогательная функция для добавления
    рецепта в избранное либо список покупок.
    """
    serializer = serializer_name(
        data={'user': request.user.id, 'recipe': instance.id, },
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_model_instance(request, model_name, instance, error_message):
    """Вспомогательная функция для удаления рецепта
    из избранного либо из списка покупок.
    """
    if not model_name.objects.filter(user=request.user,
                                     recipe=instance).exists():
        return Response({'errors': error_message},
                        status=status.HTTP_400_BAD_REQUEST)
    model_name.objects.filter(user=request.user, recipe=instance).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def create_shopping_list_report(shopping_cart):
    recipes = shopping_cart.values_list('recipe_id', flat=True)
    buy_list = RecipeIngredient.objects.filter(
        recipe__in=recipes
    ).values(
        'ingredient'
    ).annotate(
        amount=Sum('amount')
    )
    buy_list_text = 'Foodgram\nСписок покупок:\n'
    for item in buy_list:
        ingredient = Ingredient.objects.get(pk=item['ingredient'])
        amount = item['amount']
        buy_list_text += (
            f'{ingredient.name}, {amount} '
            f'{ingredient.measurement_unit}\n'
        )
    return buy_list_text