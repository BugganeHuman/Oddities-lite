from django.contrib import admin
from django.urls import path, include
from users.views import ping, backup
from criticism.views import show_titles, sort_down, sort_up
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/titles/", include("titles.urls")),
    path("api/watchlist/", include("watchlist.urls")),
    path("api/users/", include("users.urls")),
    path('api/ping/', ping),
    path('api/backup/', backup),
    path('criticism/', show_titles),
    path('criticism/sort_up/', sort_up ),
    path('criticism/sort_down/', sort_down),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
