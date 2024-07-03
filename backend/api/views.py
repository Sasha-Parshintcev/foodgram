from django.shortcuts import get_object_or_404, HttpResponse
from http import HTTPStatus
import shortuuid
from shortener.models import Url
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import (
    SAFE_METHODS,
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from .filters import RecipeFilter
from users.models import User, Subscription
from .utils import (
    create_model_instance,
    delete_model_instance,
    create_shopping_list_report
)
from food.models import (
    Tag, Ingredient, Recipe, Favorite,
    ShoppingCart
)
from .serializers import (
    UserSerializer, AvatarSerializer, TagSerializer,
    IngredientSerializer, RecipeSerializer,
    FavoriteSerializer, ShoppingCartSerializer,
    RecipeCreateSerializer, SubscriptionSerializer, SubscribeSerializer
)
from .permissions import IsAuthorOrReadOnly


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
        permission_classes=[IsAuthenticatedOrReadOnly, ]
    )
    def favorite(self, request, pk):
        """Работа с избранными рецептами.
        Удаление/добавление в избранное.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        
        if request.method == 'POST':
            return create_model_instance(request, recipe, FavoriteSerializer)

        if request.method == 'DELETE':
            error_message = 'У вас нет этого рецепта в избранном'
            return delete_model_instance(request, Favorite,
                                         recipe, error_message)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        """Работа со списком покупок.
        Удаление/добавление в список покупок.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        
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
        permission_classes=(AllowAny,),
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


class IngredientViewSet(mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet):
    """ViewSet для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    

class TagViewSet(mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet):
    """ViewSet для работы с тегами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    

class UserViewSet(djoser_views.UserViewSet):
    """Вьюсет для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(['get'], detail=False, permission_classes = (IsAuthenticated,))
    def me(self, request):
        serializer = UserSerializer(
            instance=request.user,
            context={'request': request}
        )
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
                return Response(
                    {"avatar": "http://sashamyhost.zapto.org/user.avatar.url"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
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
