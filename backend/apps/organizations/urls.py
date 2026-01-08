"""
组织架构 URL 配置
Multi-company architecture support with cross-company transfer workflows
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CompanyViewSet,
    DepartmentViewSet,
    LocationViewSet,
    OrganizationChangeViewSet,
    CrossCompanyTransferViewSet
)

router = DefaultRouter()
router.register('companies', CompanyViewSet, basename='company')
router.register('departments', DepartmentViewSet, basename='department')
router.register('locations', LocationViewSet, basename='location')
router.register('changes', OrganizationChangeViewSet, basename='organization-change')
router.register('cross-transfers', CrossCompanyTransferViewSet, basename='cross-company-transfer')

urlpatterns = [
    path('', include(router.urls)),
]
