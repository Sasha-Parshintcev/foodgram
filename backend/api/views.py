from django.shortcuts import get_object_or_404
from djoser import views as djoser_views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User, Subscription
from .serializers import UserSerializer, SubscriptionSerializer


class UserViewSet(djoser_views.UserViewSet):
    """Вьюсет для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer


    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):

        return super().me(request, *args, **kwargs)

    @action(['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        subscribing = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'user': request.user.pk,
                      'subscribing': subscribing.pk},
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = Subscription.objects.filter(user=request.user,
                                                   subscribing=subscribing)
        if subscription.exists():
            subscription.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'errors': 'Вы не были подписаны ранее!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(['get'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = User.objects.filter(
            subscribing__user=request.user).prefetch_related('recipes')
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(pages,
                                            many=True,
                                            context={'request': request})

        return self.get_paginated_response(serializer.data)


# from django.shortcuts import render
# from rest_framework import filters, status, viewsets, mixins

# from food.models import Tag, Ingredient, Recipe, RecipeIngredient, Follow
# from .serializers import (
#     TagSerializer,
#     IngredientSerializer,
#     RecipeSerializer,
#     # RecipeIngredientSerializer,
#     FollowSerializer,
#     UserSerializer
# )

# class TagViewSet(ListCreateDestroyViewSet):
#     """ViewSet для работы с тегами."""
#     queryset = Tag.objects.all()
#     serializer_class = TagSerializer
    # permission_classes
    # lookup_field = 'slug'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)


# class IngredientViewSet(ListCreateDestroyViewSet):
#     """ViewSet для работы с ингредиентами."""
#     queryset = Ingredient.objects.all()
#     serializer_class = IngredientSerializer
#     # permission_classes
#     # lookup_field = 'slug'
#     # filter_backends = (filters.SearchFilter,)
#     # search_fields = ('name',)


# class RecipeViewSet(ListCreateDestroyViewSet):
#     """ViewSet для работы с рецептом."""
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
#     # permission_classes
#     # lookup_field = 'slug'
#     # filter_backends = (filters.SearchFilter,)
#     # search_fields = ('name',)


# class FollowViewSet(
#     mixins.ListModelMixin,
#     mixins.CreateModelMixin,
#     viewsets.GenericViewSet
# ):
#     """Вьюсет фолловера."""
#     queryset = Follow.objects.all()
#     serializer_class = FollowSerializer
#     # permission_classes = (permissions.IsAuthenticated,)
#     # filter_backends = (filters.SearchFilter,)
#     search_fields = ('user__username', 'following__username',)

#     def get_queryset(self):
#         """Получение подписок."""
#         return get_object_or_404(User, username=self.request.user).follower

#     def perform_create(self, serializer):
#         """Сохраняет объект, указывая пользователя."""
#         serializer.save(user=self.request.user)


# class UserViewSet(viewsets.ModelViewSet):
#     """Вьюсет пользователя."""
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

# # class RecipeIngredientViewSet(ListCreateDestroyViewSet):
# #     """ViewSet для работы с ингредиентами."""
# #     queryset = RecipeIngredient.objects.all()
# #     serializer_class = RecipeIngredientSerializer
#     # permission_classes
#     # lookup_field = 'slug'
#     # filter_backends = (filters.SearchFilter,)
#     # search_fields = ('name',)
