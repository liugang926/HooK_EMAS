"""
用户账户 URL 配置
Multi-company architecture support
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    VerifyCredentialsView,
    CompleteLoginView,
    LogoutView,
    UserViewSet,
    RoleViewSet,
    UserRoleViewSet,
    OperationLogViewSet,
    UserCompanyMembershipViewSet
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('roles', RoleViewSet, basename='role')
router.register('user-roles', UserRoleViewSet, basename='user-role')
router.register('logs', OperationLogViewSet, basename='operation-log')
router.register('user-company-memberships', UserCompanyMembershipViewSet, basename='user-company-membership')

urlpatterns = [
    # JWT 认证
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Two-step login (more secure)
    path('verify-credentials/', VerifyCredentialsView.as_view(), name='verify_credentials'),
    path('complete-login/', CompleteLoginView.as_view(), name='complete_login'),
    
    # API 路由
    path('', include(router.urls)),
]
