from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .form_views import (
    FieldGroupViewSet,
    FieldDefinitionViewSet,
    ModuleFormConfigViewSet,
    ModuleRegistryView,
    ModuleRegistryFieldsView,
    ModuleCodeRuleView,
    ModuleFeatureView
)

router = DefaultRouter()
router.register('configs', views.SystemConfigViewSet)
router.register('logs', views.OperationLogViewSet)
router.register('code-rules', views.CodeRuleViewSet)

# Dynamic form configuration routes
router.register('form/groups', FieldGroupViewSet, basename='field-group')
router.register('form/fields', FieldDefinitionViewSet, basename='field-definition')
router.register('form/modules', ModuleFormConfigViewSet, basename='module-form-config')

urlpatterns = [
    path('', include(router.urls)),
    path('info/', views.SystemInfoView.as_view(), name='system-info'),
    path('config/', views.GlobalConfigView.as_view(), name='global-config'),
    
    # Module Registry API endpoints
    path('registry/', ModuleRegistryView.as_view(), name='module-registry'),
    path('registry/<str:module_name>/fields/', ModuleRegistryFieldsView.as_view(), name='module-registry-fields'),
    path('registry/<str:module_name>/code-rule/', ModuleCodeRuleView.as_view(), name='module-code-rule'),
    path('registry/features/', ModuleFeatureView.as_view(), name='module-features'),
]
