from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator

from .serializers import UserSerializer

сlass UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    # permission_classes = (IsAdminOrSuperuser,)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)
    # lookup_field = 'username'
    # http_method_names = ['get', 'post', 'patch', 'delete']


# class GetTokenView(APIView):
#     """Вьюсет для получения токена. Разроешены только POST запросы."""
#     permission_classes = (AllowAny,)

#     def post(self, request):
#         serializer = TokenSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         username = serializer.validated_data['username']
#         code = serializer.validated_data['confirmation_code']

#         user = get_object_or_404(User, username=username)

#         if not default_token_generator.check_token(user, code):
#             return Response({'detail': 'Неверный код'},
#                             status=status.HTTP_400_BAD_REQUEST)

#         token = AccessToken.for_user(user)
#         return Response({'token': str(token)})