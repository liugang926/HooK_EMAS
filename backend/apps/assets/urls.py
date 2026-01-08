"""
资产管理 URL 配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AssetCategoryViewSet,
    AssetViewSet,
    AssetOperationViewSet,
    AssetReceiveViewSet,
    AssetBorrowViewSet,
    AssetTransferViewSet,
    AssetDisposalViewSet,
    AssetMaintenanceViewSet,
    AssetLabelViewSet
)

router = DefaultRouter()
router.register('categories', AssetCategoryViewSet, basename='asset-category')
router.register('list', AssetViewSet, basename='asset')
router.register('operations', AssetOperationViewSet, basename='asset-operation')
router.register('receives', AssetReceiveViewSet, basename='asset-receive')
router.register('borrows', AssetBorrowViewSet, basename='asset-borrow')
router.register('transfers', AssetTransferViewSet, basename='asset-transfer')
router.register('disposals', AssetDisposalViewSet, basename='asset-disposal')
router.register('maintenances', AssetMaintenanceViewSet, basename='asset-maintenance')
router.register('labels', AssetLabelViewSet, basename='asset-label')

urlpatterns = [
    path('', include(router.urls)),
]
