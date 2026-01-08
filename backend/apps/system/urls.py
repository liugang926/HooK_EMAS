from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .form_views import FieldGroupViewSet, FieldDefinitionViewSet, ModuleFormConfigViewSet

router = DefaultRouter()
router.register('configs', views.SystemConfigViewSet)
router.register('logs', views.OperationLogViewSet)
router.register('code-rules', views.CodeRuleViewSet)

# 动态表单配置路由
router.register('form/groups', FieldGroupViewSet, basename='field-group')
router.register('form/fields', FieldDefinitionViewSet, basename='field-definition')
router.register('form/modules', ModuleFormConfigViewSet, basename='module-form-config')

urlpatterns = [
    path('', include(router.urls)),
    path('info/', views.SystemInfoView.as_view(), name='system-info'),
    path('config/', views.GlobalConfigView.as_view(), name='global-config'),
]
