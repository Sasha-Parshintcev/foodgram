from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet


api_v1 = DefaultRouter()
api_v1.register('users', UserViewSet, basename='users')
# router_v1.register(
#     'users/(?P<id>[^/.]+)/subscribe',
#     FollowViewSet, basename='subscribe'
# )

urlpatterns = [
    path('', include(api_v1.urls)),
    # path('api-token-auth/', views.obtain_auth_token),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]