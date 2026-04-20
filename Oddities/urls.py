from django.contrib import admin
from django.urls import path, include
from users.views import ping, backup
from criticism.views import show_titles, sort_down, sort_up
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
]
