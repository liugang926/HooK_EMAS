from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.ConsumableCategoryViewSet)
router.register('list', views.ConsumableViewSet)
router.register('stocks', views.ConsumableStockViewSet)
router.register('inbounds', views.ConsumableInboundViewSet)
router.register('outbounds', views.ConsumableOutboundViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
