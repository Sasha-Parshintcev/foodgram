from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from djoser import views as djoser_views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from users.models import User, Subscription
from .serializers import UserSerializer, AvatarSerializer
# SubscriptionSerializer, AuthTokenSerializer


class UserViewSet(djoser_views.UserViewSet):
    """Вьюсет для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer


    @action(['get'], detail=False)
    def me(self, request):
        serializer = self.serializer_class(request.user)
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
                return Response({'avatar_url': user.avatar.url}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            user.avatar = 'users/image.png'
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        

    # @action(['get', 'put', 'delete'], detail=False, url_path='me/avatar', permission_classes=(IsAuthenticated,))
    # @login_required
    # def avatar(self, request, user):
    #     if request.method == 'PUT':
    #         if 'avatar' not in request.data:
    #             return Response({'error': 'Не указано поле `avatar`'}, status=status.HTTP_400_BAD_REQUEST)

    #         serializer = AvatarSerializer(data=request.data)
    #         if serializer.is_valid():
    #             user.avatar = serializer.validated_data['avatar']
    #             user.save()
    #             return Response({'avatar_url': user.avatar.url}, status=status.HTTP_200_OK)
    #         else:
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     elif request.method == 'GET':
    #         return Response({'avatar_url': user.avatar.url}, status=status.HTTP_200_OK)
    #     elif request.method == 'DELETE':
    #         user.avatar = None
    #         user.save()
    #         return Response(status=status.HTTP_204_NO_CONTENT)








    # @action(['get', 'put', 'delete'], detail=False, url_path='me/avatar', permission_classes=(IsAuthenticated,))
    # @login_required
    # def avatar(self, request, user):
    #     user = request.user
    #     if request.method == 'PUT':
    #         serializer = AvatarSerializer(data=request.data)
    #         if serializer.is_valid():
    #             user.avatar = serializer.validated_data['avatar']
    #             user.save()
    #             return Response({'avatar_url': user.avatar.url}, status=status.HTTP_200_OK)
    #         else:
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     elif request.method == 'GET':
    #         return Response({'avatar_url': user.avatar.url}, status=status.HTTP_200_OK)
    #     elif request.method == 'DELETE':
    #         user.avatar = None
    #         user.save()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
        
    
    # @action(['get', 'put', 'delete'], detail=False, url_path='me/avatar', permission_classes=(IsAuthenticated,))
    # def avatar(self, request):
    #     user = request.user
    #     avatar_url = user.avatar.url_path
    #     response_data = {
    #     '/avatars': avatar_url
    #     }

    #     return Response(response_data)
    # @action(['post', 'delete'],
    #         detail=True,
    #         permission_classes=(IsAuthenticated,))
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


# class TokenUserAuth(ObtainAuthToken):
#     serializer_class = AuthTokenSerializer
#     http_method_names = ["post", ]

#     def post(self, request, *args, **kwargs):
#         use_request = request.path.split('/')[-2]
#         if use_request == 'login':
#             serializer = self.serializer_class(data=request.data,
#                                                context={'request': request})
#             serializer.is_valid(raise_exception=True)
#             user = serializer.validated_data['user']
#             token, created = Token.objects.get_or_create(user=user)

#             return Response({
#                 'auth_token': token.key,
#             })
#         elif use_request == 'logout':
#             auth = request.headers.get('Authorization')
#             if auth:
#                 token = Token.objects.filter(key=auth[6:])
#                 if token.exists():
#                     token.delete()
#                     return Response(status=204)
#                 return Response(
#                     status=404,
#                     data=dict(
#                         detail='Учетные данные не найдены'
#                     )
#                 )
#             return Response(
#                 status=401,
#                 data=dict(
#                     detail='Учетные данные не были предоставлены.'
#                 )
#             )

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