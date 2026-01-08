"""
Multi-company architecture support
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import uuid

from .models import Role, UserRole, OperationLog, UserCompanyMembership
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    RoleSerializer,
    UserRoleSerializer,
    OperationLogSerializer,
    UserCompanyMembershipSerializer,
    UserCompanyMembershipCreateSerializer
)
from .pagination import FlexiblePageNumberPagination
from .services import RoleService

User = get_user_model()


class LogoutView(APIView):
    """
    Logout endpoint - blacklists the refresh token to invalidate the session.
    """
    permission_classes = []  # Allow unauthenticated requests (for already expired tokens)
    authentication_classes = []  # Disable CSRF
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'detail': '登出成功'}, status=status.HTTP_200_OK)
        except Exception:
            # Even if token is invalid, return success (user is effectively logged out)
            return Response({'detail': '登出成功'}, status=status.HTTP_200_OK)


class VerifyCredentialsView(APIView):
    """
    Step 1 of two-step login: Verify username/password and return available companies.
    More secure as company list is only exposed after successful credential verification.
    """
    permission_classes = []  # No authentication required
    authentication_classes = []  # Disable CSRF checking for login endpoint
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': '请提供用户名和密码'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            return Response(
                {'error': '用户名或密码错误'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': '账号已被禁用'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get user's available companies
        from apps.organizations.models import Company
        
        companies = []
        
        # 1. Check UserCompanyMembership (multi-company support)
        memberships = UserCompanyMembership.objects.filter(
            user=user,
            end_date__isnull=True
        ).select_related('company').order_by('-membership_type', 'company__name')
        
        company_ids = set()
        for membership in memberships:
            if membership.company.is_active and membership.company_id not in company_ids:
                companies.append({
                    'id': membership.company.id,
                    'name': membership.company.name,
                    'short_name': membership.company.short_name,
                    'membership_type': membership.membership_type
                })
                company_ids.add(membership.company_id)
        
        # 2. If no memberships, check user's direct company assignment
        if not companies and hasattr(user, 'company') and user.company:
            companies.append({
                'id': user.company.id,
                'name': user.company.name,
                'short_name': user.company.short_name,
                'membership_type': 'primary'
            })
        
        # 3. For superusers with no company, return all active companies
        if not companies and user.is_superuser:
            all_companies = Company.objects.filter(is_active=True).values(
                'id', 'name', 'short_name'
            )
            companies = [
                {**c, 'membership_type': 'admin'} for c in all_companies
            ]
        
        # 4. If still no companies, return error
        if not companies:
            return Response(
                {'error': '您没有关联任何公司，请联系管理员'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate temp token (valid for 30 minutes)
        temp_token = str(uuid.uuid4())
        cache_key = f'login_temp_token:{temp_token}'
        cache.set(cache_key, {
            'user_id': user.id,
            'username': user.username,
            'company_ids': [c['id'] for c in companies]
        }, timeout=1800)  # 30 minutes
        
        return Response({
            'temp_token': temp_token,
            'username': user.username,
            'display_name': user.display_name or user.username,
            'companies': companies
        })


class CompleteLoginView(APIView):
    """
    Step 2 of two-step login: Complete login with selected company.
    """
    permission_classes = []  # No authentication required
    authentication_classes = []  # Disable CSRF
    
    def post(self, request):
        temp_token = request.data.get('temp_token')
        company_id = request.data.get('company_id')
        
        if not temp_token or not company_id:
            return Response(
                {'error': '请提供 temp_token 和 company_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify temp token
        cache_key = f'login_temp_token:{temp_token}'
        token_data = cache.get(cache_key)
        
        if not token_data:
            return Response(
                {'error': '验证已过期，请重新登录'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify company access
        if company_id not in token_data['company_ids']:
            return Response(
                {'error': '您没有该公司的访问权限'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get user
        try:
            user = User.objects.get(id=token_data['user_id'])
        except User.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Delete temp token (one-time use)
        cache.delete(cache_key)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Record login log
        try:
            from apps.system.logging import record_log
            request.user = user
            record_log(request, 'system', 'login', f'用户 {user.username} 登录系统')
        except Exception as e:
            print(f"记录登录日志失败: {e}")
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'display_name': user.display_name or user.username
            }
        })


class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义登录视图"""
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # 记录登录日志
        if response.status_code == 200:
            try:
                from apps.system.logging import record_log
                username = request.data.get('username', '')
                user = User.objects.filter(username=username).first()
                if user:
                    # 临时设置 user 到 request 以便记录
                    request.user = user
                record_log(request, 'system', 'login', f'用户 {username} 登录系统')
            except Exception as e:
                print(f"记录登录日志失败: {e}")
        
        return response


class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图集"""
    
    queryset = User.objects.select_related('department').all()
    serializer_class = UserSerializer
    pagination_class = FlexiblePageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'department', 'sso_type']
    search_fields = ['username', 'first_name', 'last_name', 'employee_no', 'phone', 'email', 'nickname']
    ordering_fields = ['created_at', 'username', 'employee_no']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """更新当前用户资料"""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码"""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': '密码修改成功'})
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """重置用户密码"""
        user = self.get_object()
        new_password = request.data.get('new_password', '123456')
        user.set_password(new_password)
        user.save()
        return Response({'message': f'密码已重置为: {new_password}'})
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换用户激活状态"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        status_text = '已激活' if user.is_active else '已禁用'
        return Response({'message': f'用户{status_text}'})


class RoleViewSet(viewsets.ModelViewSet):
    """角色管理视图集"""
    
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['is_active', 'is_system']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    
    def destroy(self, request, *args, **kwargs):
        role = self.get_object()
        if role.is_system:
            return Response(
                {'error': '系统角色不能删除'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """获取角色成员列表"""
        role = self.get_object()
        user_roles = UserRole.objects.filter(role=role).select_related(
            'user', 'user__department'
        )
        members = []
        for ur in user_roles:
            members.append({
                'id': ur.user.id,
                'user_role_id': ur.id,
                'name': ur.user.display_name or ur.user.username,
                'department': ur.user.department.name if ur.user.department else '-',
                'position': ur.user.position or '-',
                'phone': ur.user.phone or '-'
            })
        return Response(members)
    
    @action(detail=True, methods=['post'])
    def add_members(self, request, pk=None):
        """批量添加角色成员"""
        role = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        added_count = 0
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                _, created = UserRole.objects.get_or_create(
                    user=user,
                    role=role,
                    defaults={'department': user.department}
                )
                if created:
                    added_count += 1
            except User.DoesNotExist:
                continue
        
        return Response({
            'message': f'成功添加 {added_count} 个成员',
            'added_count': added_count
        })
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """移除角色成员"""
        role = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': '请提供用户ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        deleted, _ = UserRole.objects.filter(role=role, user_id=user_id).delete()
        
        if deleted:
            return Response({'message': '成员已移除'})
        return Response({'error': '成员不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def sync_roles(self, request):
        """
        同步所有用户角色
        - 所有活跃用户分配普通员工角色
        - 部门负责人分配部门管理员角色
        - 超级用户分配超级管理员角色
        """
        stats = RoleService.sync_all_user_roles()
        
        if 'error' in stats:
            return Response({'error': stats['error']}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': '角色同步完成',
            'stats': stats
        })
    
    @action(detail=False, methods=['post'])
    def init_default_roles(self, request):
        """初始化默认角色"""
        created_roles = RoleService.ensure_default_roles()
        
        return Response({
            'message': f'成功创建 {len(created_roles)} 个默认角色',
            'created_roles': [r.name for r in created_roles]
        })


class UserRoleViewSet(viewsets.ModelViewSet):
    """用户角色管理视图集"""
    
    queryset = UserRole.objects.select_related('user', 'role', 'department').all()
    serializer_class = UserRoleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'role', 'department']


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """操作日志视图集（只读）"""
    
    queryset = OperationLog.objects.select_related('user').all()
    serializer_class = OperationLogSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'operation_type', 'module']
    search_fields = ['description', 'request_path']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class UserCompanyMembershipViewSet(viewsets.ModelViewSet):
    """
    用户公司关联视图集
    Manage user's company memberships for multi-company support
    """
    
    queryset = UserCompanyMembership.objects.select_related(
        'user', 'company', 'department', 'created_by'
    ).all()
    serializer_class = UserCompanyMembershipSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'company', 'membership_type', 'is_admin', 'data_scope']
    search_fields = ['user__username', 'user__nickname', 'company__name']
    ordering_fields = ['created_at', 'start_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCompanyMembershipCreateSerializer
        return UserCompanyMembershipSerializer
    
    def get_queryset(self):
        """Filter by company if provided"""
        queryset = super().get_queryset()
        company_id = self.request.query_params.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Only show active memberships by default
        show_inactive = self.request.query_params.get('show_inactive', 'false')
        if show_inactive.lower() != 'true':
            queryset = queryset.filter(end_date__isnull=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_companies(self, request):
        """Get current user's company memberships"""
        memberships = self.queryset.filter(
            user=request.user,
            end_date__isnull=True
        )
        serializer = self.get_serializer(memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get all company memberships for a specific user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': '请提供 user_id 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        memberships = self.queryset.filter(user_id=user_id)
        serializer = self.get_serializer(memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_company(self, request):
        """Get all user memberships for a specific company"""
        company_id = request.query_params.get('company_id')
        if not company_id:
            return Response(
                {'error': '请提供 company_id 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        memberships = self.queryset.filter(
            company_id=company_id,
            end_date__isnull=True
        )
        serializer = self.get_serializer(memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def end_membership(self, request, pk=None):
        """End a user's company membership"""
        membership = self.get_object()
        
        from django.utils import timezone
        membership.end_date = timezone.now().date()
        membership.save()
        
        return Response({
            'message': '公司关联已结束',
            'end_date': membership.end_date
        })
    
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def batch_assign(self, request):
        """
        Batch assign users to a company
        Request body: {
            "company_id": 1,
            "user_ids": [1, 2, 3],
            "membership_type": "secondary",
            "department_id": 1 (optional)
        }
        """
        company_id = request.data.get('company_id')
        user_ids = request.data.get('user_ids', [])
        membership_type = request.data.get('membership_type', 'secondary')
        department_id = request.data.get('department_id')
        
        if not company_id or not user_ids:
            return Response(
                {'error': '请提供 company_id 和 user_ids'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.organizations.models import Company
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {'error': '公司不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        created_count = 0
        skipped_count = 0
        
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                _, created = UserCompanyMembership.objects.get_or_create(
                    user=user,
                    company=company,
                    membership_type=membership_type,
                    defaults={
                        'department_id': department_id,
                        'created_by': request.user
                    }
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1
            except User.DoesNotExist:
                continue
        
        return Response({
            'message': f'成功分配 {created_count} 个用户，跳过 {skipped_count} 个已存在的',
            'created_count': created_count,
            'skipped_count': skipped_count
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get membership statistics"""
        company_id = request.query_params.get('company_id')
        
        base_qs = self.queryset.filter(end_date__isnull=True)
        if company_id:
            base_qs = base_qs.filter(company_id=company_id)
        
        stats = {
            'total': base_qs.count(),
            'by_type': {},
            'by_data_scope': {},
            'admin_count': base_qs.filter(is_admin=True).count(),
            'finance_access_count': base_qs.filter(can_view_finance=True).count()
        }
        
        for choice in UserCompanyMembership.MembershipType.choices:
            stats['by_type'][choice[0]] = base_qs.filter(membership_type=choice[0]).count()
        
        for choice in UserCompanyMembership.DataScope.choices:
            stats['by_data_scope'][choice[0]] = base_qs.filter(data_scope=choice[0]).count()
        
        return Response(stats)
