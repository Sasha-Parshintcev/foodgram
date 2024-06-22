from django.shortcuts import get_object_or_404, HttpResponse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
# from shortener import create_short_link
from shortener import shortener
# from django.contrib.auth.decorators import login_required
# from food.models import Shortener
# from .utils import shortener
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.core.exceptions import PermissionDenied
# from rest_framework.authtoken.models import Token
# from rest_framework.authtoken.views import ObtainAuthToken

from .filters import RecipeFilter
from users.models import User
# , Subscription
from .utils import create_model_instance, delete_model_instance
from food.models import (
    Tag, Ingredient, Recipe, Favorite,
    ShoppingCart, RecipeIngredient
    # , RecipeLink
)
from .serializers import (
    UserSerializer, AvatarSerializer, TagSerializer,
    IngredientSerializer, RecipeSerializer,
    FavoriteSerializer, ShoppingCartSerializer, RecipeCreateSerializer
    # , RecipeLinkSerializer
)
from .permissions import IsAuthorOrReadOnly
# SubscriptionSerializer, AuthTokenSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'ingredients', 'tags'
        ).all()
        return recipes
    
    def perform_create(self, serializer):
        """Сохранение автора при создании рецепта."""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer
    
    @action(
        methods=['get'],
        detail=True,
        url_path='get-link',
        url_name='get-link',
        # permission_classes=IsAuthenticatedOrReadOnly,
    )
    def get_link(self, request, pk=None):
        # recipe = Recipe.objects.get(id=pk)
        original_url = 'http://sashamyhost.zapto.org/api/recipes/'  #recipe.url   
        short_link = shortener.create(request.user, original_url)
        return Response({'short-link': short_link })

    # @action(
    #     detail=True,
    #     methods=['post', 'delete'],
    #     permission_classes=[IsAuthenticated, ]
    # )
    # def favorite(self, request, pk):
    #     """Работа с избранными рецептами.
    #     Удаление/добавление в избранное.
    #     """
    #     recipe = get_object_or_404(Recipe, id=pk)
    #     if request.method == 'POST':
    #         return create_model_instance(request, recipe, FavoriteSerializer)

    #     if request.method == 'DELETE':
    #         error_message = 'У вас нет этого рецепта в избранном'
    #         return delete_model_instance(request, Favorite,
    #                                      recipe, error_message)

    # @action(
    #     detail=True,
    #     methods=['post', 'delete'],
    #     permission_classes=[IsAuthenticated, ]
    # )
    # def shopping_cart(self, request, pk):
    #     """Работа со списком покупок.
    #     Удаление/добавление в список покупок.
    #     """
    #     recipe = get_object_or_404(Recipe, id=pk)
    #     if request.method == 'POST':
    #         return create_model_instance(request, recipe,
    #                                      ShoppingCartSerializer)

    #     if request.method == 'DELETE':
    #         error_message = 'У вас нет этого рецепта в списке покупок'
    #         return delete_model_instance(request, ShoppingCart,
    #                                      recipe, error_message)

    # @action(
    #     detail=False,
    #     methods=['get'],
    #     permission_classes=[IsAuthenticated, ]
    # )
    # def download_shopping_cart(self, request):
    #     """Отправка файла со списком покупок."""
    #     ingredients = RecipeIngredient.objects.filter(
    #         recipe__carts__user=request.user
    #     ).values(
    #         'ingredient__name', 'ingredient__measurement_unit'
    #     ).annotate(ingredient_amount=Sum('amount'))
    #     shopping_list = ['Список покупок:\n']
    #     for ingredient in ingredients:
    #         name = ingredient['ingredient__name']
    #         unit = ingredient['ingredient__measurement_unit']
    #         amount = ingredient['ingredient_amount']
    #         shopping_list.append(f'\n{name} - {amount}, {unit}')
    #     response = HttpResponse(shopping_list, content_type='text/plain')
    #     response['Content-Disposition'] = \
    #         'attachment; filename="shopping_cart.txt"'
    #     return response


# class RecipeViewSet(viewsets.ModelViewSet):
#     """ViewSet для работы с рецептом."""
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
    # permission_classes
    # lookup_field = 'slug'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)

# class (viewsets.ViewSet):
#     queryset = RecipeLink.objects.all()
#     serializer_class = RecipeLinkSerializer

#     def create(self, request):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             original_url = serializer.validated_data.get('original_url')
#             short_url = shortener.get_short_url(original_url)  # Генерация короткой ссылки
#             serializer.save(short_url=short_url)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def list(self, request):
#         queryset = RecipeLink.objects.all()
#         serializer = RecipeLinkSerializer(queryset, many=True)
#         return ResponseRecipeLinkViewSet(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = RecipeLink.objects.all()
#         recipe = get_object_or_404(queryset, pk=pk)
#         serializer = RecipeLinkSerializer(recipe)
#         return Response(serializer.data)

#     def update(self, request, pk=None):
#         recipe = RecipeLink.objects.get(pk=pk)
#         serializer = RecipeLinkSerializer(recipe, data=request.data, partial=True)
#         if serializer.is_valid():
#             short_url = shortener.get_short_url(serializer.validated_data.get('original_url'))  # Генерация короткой ссылки
#             serializer.save(short_url=short_url)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngredientViewSet(mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet):
    """ViewSet для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    # permission_classes
    # lookup_field = 'slug'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)

class TagViewSet(mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet):
    """ViewSet для работы с тегами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    # permission_classes
    # lookup_field = 'slug'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)

    # def tag_list(data):
    #     serializer = TagListSerializer(data=data)
    #     serializer.is_valid(raise_exception=True)
    #     tags = serializer.validated_data['tags']
    #     return tags

class UserViewSet(djoser_views.UserViewSet):
    """Вьюсет для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    # pagination_class = LimitOffsetPagination



    @action(['get'], detail=False, permission_classes = (IsAuthenticated,))
    def me(self, request):
        serializer = UserSerializer(instance=request.user, context={'request': request})
        return Response(serializer.data)

    @action(methods=['put', 'delete'], detail=False, url_path='me/avatar')
    def avatar(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'detail': 'Учетные данные аутентификации не предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = AvatarSerializer(data=request.data)
        if request.method == 'PUT':
            if serializer.is_valid():
                user.avatar = serializer.validated_data['avatar']
                user.save()
                return Response({"avatar": "http://sashamyhost.zapto.org/user.avatar.url"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    # def subscribe(self, request, id):
    #     subscribing = get_object_or_404(User, pk=id)

    #     if request.method == 'POST':
    #         serializer = SubscriptionSerializer(
    #             data={'user': request.user.pk,
    #                   'subscribing': subscribing.pk},
    #             context={'request': request})
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()

    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

    #     subscription = Subscription.objects.filter(user=request.user,
    #                                                subscribing=subscribing)
    #     if subscription.exists():
    #         subscription.delete()

    #         return Response(status=status.HTTP_204_NO_CONTENT)

    #     return Response({'errors': 'Вы не были подписаны ранее!'},
    #                     status=status.HTTP_400_BAD_REQUEST)

    # @action(['get'],
    #         detail=False,
    #         permission_classes=(IsAuthenticated,))
    # def subscriptions(self, request):
    #     queryset = User.objects.filter(
    #         subscribing__user=request.user).prefetch_related('recipes')
    #     pages = self.paginate_queryset(queryset)
    #     serializer = SubscriptionSerializer(pages,
    #                                         many=True,
    #                                         context={'request': request})

    #     return self.get_paginated_response(serializer.data)



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


# class SubscriptionViewSet(
#     mixins.ListModelMixin,
#     mixins.CreateModelMixin,
#     viewsets.GenericViewSet
# ):
#     """Вьюсет фолловера."""
#     queryset = Subscription.objects.all()
#     serializer_class = SubscriptionSerializer
#     # permission_classes = (permissions.IsAuthenticated,)
#     # filter_backends = (filters.SearchFilter,)
#     search_fields = ('user__username', 'author__username',)

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