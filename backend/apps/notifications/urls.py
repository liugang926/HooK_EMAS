from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('messages', views.NotificationViewSet)
router.register('announcements', views.AnnouncementViewSet)
router.register('alert-rules', views.AlertRuleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
