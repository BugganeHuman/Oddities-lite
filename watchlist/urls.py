from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WatchlistItemViewSet, order_by

router = DefaultRouter()
router.register(r"item", WatchlistItemViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('order_by/', order_by, name='order_by'),
]