from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('tasks', views.InventoryTaskViewSet)
router.register('records', views.InventoryRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
