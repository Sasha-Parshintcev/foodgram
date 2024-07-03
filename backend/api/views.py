from django.shortcuts import get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
# from shortener import create_short_link
# from shortener import shortener
from http import HTTPStatus
import shortuuid
from shortener.models import Url
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

# У тебя получилось пройти тесты на короткие ссылки? Я чет
# когда пытался выполнить миграции, то ругалось на конфликты созданных миграций
# в самой библиотеке shortener. Я уже мержил, переименовывал их, потому что импортируем модель Url,
# а в последних миграциях там другое значение ключа
from .filters import RecipeFilter
from users.models import User, Subscription
# 
from .utils import create_model_instance, delete_model_instance, create_shopping_list_report
from food.models import (
    Tag, Ingredient, Recipe, Favorite,
    ShoppingCart, RecipeIngredient
    # , RecipeLink
)
from .serializers import (
    UserSerializer, AvatarSerializer, TagSerializer,
    IngredientSerializer, RecipeSerializer,
    FavoriteSerializer, ShoppingCartSerializer, RecipeCreateSerializer, SubscriptionSerializer, SubscribeSerializer
    # , RecipeLinkSerializer
)
from .permissions import IsAuthorOrReadOnly
# 

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
        # elif self.action == 'is_favorited':
        #     return FavoriteSerializer
        return RecipeCreateSerializer
    
    @action(
        methods=['get'],
        detail=True,
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        long_url = request.build_absolute_uri(f'/recipes/{recipe.pk}/')
        short_id = shortuuid.uuid()[:6]
        short_url = Url.objects.create(long_url=long_url, short_id=short_id)   
        short_link = request.build_absolute_uri(f'/s/{short_url.short_id}/')
        return Response({'short-link': short_link }, status=HTTPStatus.OK)


    @action(
        detail=True,
        methods=['get', 'post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        """Работа с избранными рецептами.
        Удаление/добавление в избранное.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        # if request.method == 'GET':
        #     return 
        
        if request.method == 'POST':
            return create_model_instance(request, recipe, FavoriteSerializer)

        if request.method == 'DELETE':
            error_message = 'У вас нет этого рецепта в избранном'
            return delete_model_instance(request, Favorite,
                                         recipe, error_message)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticatedOrReadOnly, ]
    )
    def shopping_cart(self, request, pk):
        """Работа со списком покупок.
        Удаление/добавление в список покупок.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        # if request.method == 'GET':
        #     return create_model_instance(request, recipe,
        #                                  ShoppingCartSerializer)
        
        if request.method == 'POST':
            return create_model_instance(request, recipe,
                                         ShoppingCartSerializer)

        if request.method == 'DELETE':
            error_message = 'У вас нет этого рецепта в списке покупок'
            return delete_model_instance(request, ShoppingCart,
                                         recipe, error_message)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Отправка файла со списком покупок."""

        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        buy_list_text = create_shopping_list_report(shopping_cart)
        response = HttpResponse(buy_list_text, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response

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
    #         measurement_unit = ingredient['ingredient__measurement_unit']
    #         amount = ingredient['ingredient__amount']
    #         shopping_list.append(f'\n{name} - {amount}, {measurement_unit}')
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
    permission_classes = (IsAuthenticatedOrReadOnly,)
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

    @action(
        methods=('get',),
        detail=False,
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated,),
        pagination_class=LimitOffsetPagination
    )
    def subscriptions(self, request):
        """Просмотр подписок пользователя."""

        user = request.user
        subscriptions = user.follower.all()
        users_id = subscriptions.values_list('author_id', flat=True)
        users = User.objects.filter(id__in=users_id)
        paginated_queryset = self.paginate_queryset(users)
        serializer = self.serializer_class(paginated_queryset,
                                           context={'request': request},
                                           many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=('post', 'delete'),
            serializer_class=SubscribeSerializer,
            permission_classes=(IsAuthenticated,),
            )
    def subscribe(self, request, id=None):
        """Добавление и удаление подписок пользователя."""

        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request, 'id': id}
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=id)
            return Response(response_data, status=status.HTTP_201_CREATED)
                # {}, #'message': 'Подписка успешно создана', 'data': 
                 
                
            # )
        elif request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription, user=self.request.user,
                author=get_object_or_404(User, id=id)
            )
            subscription.delete()
            return Response(
                {'Успешная отписка'},
                status=status.HTTP_204_NO_CONTENT
            )

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