from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TitleViewSet, get_revisits, order_by

router = DefaultRouter()
router.register(r"title", TitleViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('revisits', get_revisits, name='get_revisits'),
    path('order_by/', order_by, name='order_by'),
]


