from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('templates', views.WorkflowTemplateViewSet)
router.register('instances', views.WorkflowInstanceViewSet)
router.register('tasks', views.WorkflowTaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
