from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('suppliers', views.SupplierViewSet)
router.register('requests', views.PurchaseRequestViewSet)
router.register('orders', views.PurchaseOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
