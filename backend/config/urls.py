from django.conf import settings
from django.conf.urls.static import static
# from django.conf.urls.media import media
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include ('api.urls')),
    # path('api-auth/', include('rest_framework.urls')),
    # path('api-token-auth/', views.obtain_auth_token),
    # path('auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.jwt')),
]

if settings.DEBUG:
    urlpatterns = (
        urlpatterns
        + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
