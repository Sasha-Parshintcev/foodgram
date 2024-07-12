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
    create_shopping_list
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
    """
    Данный вьюсет отвечает за управление рецептами в Вашем приложении.
    Он предоставляет стандартные методы для
    создания, чтения, обновления и удаления рецептов.

    Разрешения: Для чтения рецептов доступ открыт для всех пользователей,
    а для создания, обновления и удаления рецептов требуется авторизация.
    Кроме того, пользователь должен быть автором рецепта,
    чтобы иметь право на его изменение или удаление.

    Фильтрация: Для фильтрации рецептов используется класс RecipeFilter,
    который позволяет фильтровать по различным критериям.

    Методы HTTP: Поддерживаются методы GET, POST, PATCH и DELETE.
    """
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        """
        Переопределяет стандартный метод get_queryset,
        чтобы предварительно загрузить связанные объекты ingredients и tags
        для каждого рецепта. Это позволяет оптимизировать
        количество запросов к базе данных.
        """
        return Recipe.objects.prefetch_related('ingredients', 'tags').all()

    def perform_create(self, serializer):
        """Переопределяет стандартный метод perform_create,
        чтобы автоматически назначать текущего пользователя
        в качестве автора при создании рецепта."""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Переопределяет стандартный метод perform_update,
        чтобы автоматически назначать текущего пользователя в качестве автора
        при обновлении рецепта."""
        serializer.save(author=self.request.user)

    def get_serializer_class(self, *args, **kwargs):
        """
        Переопределяет стандартный метод get_serializer_class,
        чтобы использовать RecipeSerializer для безопасных методов HTTP
        (GET, HEAD, OPTIONS) и RecipeCreateSerializer для небезопасных методов
        (POST, PATCH, DELETE). Это позволяет контролировать,
        какие поля доступны для чтения и записи.
        """
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        """
        Данный метод генерирует короткую ссылку
        для конкретного рецепта. Он принимает запрос на GET и
        возвращает короткую ссылку в формате JSON.
        """
        recipe = self.get_object()
        long_url = request.build_absolute_uri(
            f'/recipes/{recipe.pk}/'
        )
        short_id = shortuuid.uuid()[:6]
        short_url = Url.objects.create(
            long_url=long_url,
            short_id=short_id
        )
        short_link = request.build_absolute_uri(
            f'/s/{short_url.short_id}/'
        )
        return Response(
            {'short-link': short_link},
            status=HTTPStatus.OK
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """
        Данный метод позволяет пользователям добавлять рецепты в избранное и
        удалять их из избранного. Он поддерживает методы POST и DELETE.
        """
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            return create_model_instance(
                request,
                recipe,
                FavoriteSerializer
            )

        if request.method == 'DELETE':
            return delete_model_instance(
                request,
                Favorite,
                recipe
            )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """
        Данный метод позволяет пользователям добавлять рецепты
        в список покупок и удалять их из списка.
        Он поддерживает методы POST и DELETE.
        """
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            return create_model_instance(
                request,
                recipe,
                ShoppingCartSerializer
            )

        if request.method == 'DELETE':
            return delete_model_instance(
                request,
                ShoppingCart,
                recipe
            )

    @action(
        detail=False,
        permission_classes=(AllowAny,),
    )
    def download_shopping_cart(self, request):
        """
        Данный метод позволяет пользователям скачать текстовый файл
        со списком ингредиентов, необходимых для рецептов, добавленных
        в список покупок. Метод поддерживает только GET запросы.
        """

        user_id = self.request.user.id
        shopping_cart_items = ShoppingCart.objects.filter(
            user=user_id
        )
        buy_list_text = create_shopping_list(
            shopping_cart_items
        )
        response = HttpResponse(
            buy_list_text,
            content_type="text/plain"
        )
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list_ingredients.txt'
        )
        return response


class IngredientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Вьюсет для работы с ингредиентами.

    Реализует следующие действия:
    - Получение списка всех ингредиентов (list)
    - Получение детальной информации об одном ингредиенте (retrieve)

    Особенности:
    - Используется модель Ingredient
    - Применяется сериализатор IngredientSerializer
    - Отключена постраничная навигация (pagination_class = None)
    - Доступ разрешен для всех пользователей (permission_classes = (AllowAny,))
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Вьюсет для работы с тегами.

    Реализует следующие действия:
    - Получение списка всех ингредиентов (list)
    - Получение детальной информации об одном ингредиенте (retrieve)

    Особенности:
    - Используется модель Tag
    - Применяется сериализатор TagSerializer
    - Отключена постраничная навигация (pagination_class = None)
    - Доступ разрешен для всех пользователей (permission_classes = (AllowAny,))
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class UserViewSet(djoser_views.UserViewSet):
    """
    Вьюсет для работы с пользователями.

    Реализует следующие действия:
    - Получение информации о текущем пользователе
    - Обновление аватара
    - просмотреть список подписок пользователя и подписаться/отписаться
      от других пользователей.

    Особенности:
    - Используется модель User
    - Применяется сериализатор UserSerializer
    - Доступ разрешен для всех пользователей на чтение и
      для аутентифицированных на изменение
      (permission_classes = (IsAuthenticatedOrReadOnly,))
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """
        Получить информацию о текущем пользователе.

        Возвращает данные текущего пользователя в формате JSON.
        """
        serializer = UserSerializer(
            instance=request.user,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        methods=('put', 'delete'),
        detail=False,
        url_path='me/avatar'
    )
    def avatar(self, request):
        """
        Обновить или удалить аватар текущего пользователя.

        Принимает данные аватара в формате JSON и обновляет аватар текущего
        пользователя. Если передается метод DELETE, то аватар удаляется.
        """
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
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated,),
        pagination_class=LimitOffsetPagination
    )
    def subscriptions(self, request):
        """
        Получить список подписок текущего пользователя.

        Возвращает список пользователей,
        на которых подписан текущий пользователь,
        с использованием пагинации.
        """

        user = request.user
        subscriptions = user.follower.all()
        users_id = subscriptions.values_list(
            'author_id',
            flat=True
        )
        users = User.objects.filter(id__in=users_id)
        paginated_queryset = self.paginate_queryset(users)
        serializer = self.serializer_class(
            paginated_queryset,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        serializer_class=SubscribeSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        """
        Подписаться или отписаться от пользователя.

        Принимает ID пользователя, на которого необходимо подписаться или
        от которого необходимо отписаться. Возвращает соответствующий ответ.
        """

        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context={'request': request, 'id': id}
            )
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save(id=id)
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=request.user,
                author=get_object_or_404(User, id=id)
            )

            if not subscription.exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscription.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
