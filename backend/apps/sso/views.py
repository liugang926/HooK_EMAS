from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone

from .models import SSOConfig, SSOUserBinding, SSOSyncLog
from .services import WeWorkService, DingTalkService, FeishuService
from apps.organizations.models import Department
from apps.accounts.models import User


class WeWorkAuthView(APIView):
    """企业微信SSO认证"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """获取企业微信登录URL"""
        redirect_uri = request.query_params.get('redirect_uri', '')
        try:
            config = SSOConfig.objects.get(provider='wework', is_enabled=True)
            service = WeWorkService(config)
            login_url = service.get_auth_url(redirect_uri)
            return Response({'url': login_url})
        except SSOConfig.DoesNotExist:
            return Response({'error': '企业微信SSO未配置'}, status=status.HTTP_400_BAD_REQUEST)


class WeWorkCallbackView(APIView):
    """企业微信SSO回调"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        code = request.query_params.get('code')
        state = request.query_params.get('state')
        
        if not code:
            return Response({'error': '授权码缺失'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            config = SSOConfig.objects.get(provider='wework', is_enabled=True)
            service = WeWorkService(config)
            
            # 获取用户信息
            user_info = service.get_user_info(code)
            
            # 查找或创建用户
            user = service.get_or_create_user(user_info)
            
            # 生成JWT token
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'avatar': user.avatar
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DingTalkAuthView(APIView):
    """钉钉SSO认证"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        redirect_uri = request.query_params.get('redirect_uri', '')
        try:
            config = SSOConfig.objects.get(provider='dingtalk', is_enabled=True)
            service = DingTalkService(config)
            login_url = service.get_auth_url(redirect_uri)
            return Response({'url': login_url})
        except SSOConfig.DoesNotExist:
            return Response({'error': '钉钉SSO未配置'}, status=status.HTTP_400_BAD_REQUEST)


class DingTalkCallbackView(APIView):
    """钉钉SSO回调"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        auth_code = request.query_params.get('authCode')
        
        if not auth_code:
            return Response({'error': '授权码缺失'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            config = SSOConfig.objects.get(provider='dingtalk', is_enabled=True)
            service = DingTalkService(config)
            
            user_info = service.get_user_info(auth_code)
            user = service.get_or_create_user(user_info)
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'avatar': user.avatar
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FeishuAuthView(APIView):
    """飞书SSO认证"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        redirect_uri = request.query_params.get('redirect_uri', '')
        try:
            config = SSOConfig.objects.get(provider='feishu', is_enabled=True)
            service = FeishuService(config)
            login_url = service.get_auth_url(redirect_uri)
            return Response({'url': login_url})
        except SSOConfig.DoesNotExist:
            return Response({'error': '飞书SSO未配置'}, status=status.HTTP_400_BAD_REQUEST)


class FeishuCallbackView(APIView):
    """飞书SSO回调"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        code = request.query_params.get('code')
        
        if not code:
            return Response({'error': '授权码缺失'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            config = SSOConfig.objects.get(provider='feishu', is_enabled=True)
            service = FeishuService(config)
            
            user_info = service.get_user_info(code)
            user = service.get_or_create_user(user_info)
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'avatar': user.avatar
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SyncOrganizationView(APIView):
    """同步组织架构"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        provider = request.data.get('provider')
        
        # 获取同步选项
        sync_options = {
            'sync_type': request.data.get('sync_type', 'full'),  # full | incremental
            'clear_existing': request.data.get('clear_existing', False),  # 是否清空现有数据
            'sync_departments': request.data.get('sync_departments', True),  # 同步部门
            'sync_users': request.data.get('sync_users', True),  # 同步用户
            'sync_managers': request.data.get('sync_managers', True),  # 同步部门负责人
        }
        
        try:
            config = SSOConfig.objects.get(provider=provider, is_enabled=True)
            
            # 创建同步日志
            sync_log = SSOSyncLog.objects.create(
                sso_config=config,
                sync_type=sync_options['sync_type'],
                status='running',
                created_by=request.user,
                detail={'options': sync_options}
            )
            
            if provider == 'wework':
                service = WeWorkService(config)
            elif provider == 'dingtalk':
                service = DingTalkService(config)
            elif provider == 'feishu':
                service = FeishuService(config)
            else:
                return Response({'error': '不支持的平台'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 同步部门和员工
            result = service.sync_organization(options=sync_options)
            
            # 更新同步日志
            sync_log.status = 'success'
            sync_log.total_count = result.get('departments', 0) + result.get('users', 0) + result.get('managers', 0)
            sync_log.success_count = sync_log.total_count
            sync_log.detail = {
                'options': sync_options,
                'result': result
            }
            sync_log.completed_at = timezone.now()
            sync_log.save()
            
            # 更新配置的最后同步时间
            config.last_sync_at = timezone.now()
            config.save()
            
            return Response({
                'message': '同步成功',
                'departments': result.get('departments', 0),
                'users': result.get('users', 0),
                'managers': result.get('managers', 0)
            })
        except SSOConfig.DoesNotExist:
            return Response({'error': 'SSO未配置或未启用'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if 'sync_log' in locals():
                sync_log.status = 'failed'
                sync_log.error_message = str(e)
                sync_log.completed_at = timezone.now()
                sync_log.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SSOConfigView(APIView):
    """SSO配置管理 - Enhanced for multi-company support"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取SSO配置列表"""
        provider = request.query_params.get('provider')
        company_id = request.query_params.get('company')
        
        queryset = SSOConfig.objects.select_related('company').all()
        if provider:
            queryset = queryset.filter(provider=provider)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        configs = []
        for config in queryset:
            configs.append({
                'id': config.id,
                'company': config.company_id,
                'company_name': config.company.name if config.company else None,
                'provider': config.provider,
                'provider_display': config.get_provider_display(),
                # Core credentials
                'corp_id': config.corp_id,
                'agent_id': config.agent_id,
                'app_id': config.app_id,
                # Note: app_secret is not returned for security
                # OAuth settings
                'oauth_enabled': config.oauth_enabled,
                'callback_url': config.callback_url,
                # Sync settings
                'sync_enabled': config.sync_enabled,
                'sync_departments': config.sync_departments,
                'sync_users': config.sync_users,
                'sync_interval': config.sync_interval,
                'root_department_id': config.root_department_id,
                # User creation settings
                'auto_create_user': config.auto_create_user,
                'auto_create_department': config.auto_create_department,
                'default_role_id': config.default_role_id,
                # Status
                'is_enabled': config.is_enabled,
                'auto_sync': config.auto_sync,
                'extra_config': config.extra_config,
                'last_sync_at': config.last_sync_at,
                'created_at': config.created_at,
                'updated_at': config.updated_at
            })
        
        return Response(configs)
    
    def post(self, request):
        """保存SSO配置"""
        provider = request.data.get('provider')
        # Support both 'company' and 'company_id' for backwards compatibility
        company_id = request.data.get('company') or request.data.get('company_id', 1)
        
        from apps.organizations.models import Company
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'msg': '公司不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Build defaults dict with all supported fields
        defaults = {
            'is_enabled': request.data.get('is_enabled', True),
            'auto_sync': request.data.get('auto_sync', False),
            'extra_config': request.data.get('extra_config', {}),
        }
        
        # Core credentials - only update if provided
        if 'corp_id' in request.data:
            defaults['corp_id'] = request.data.get('corp_id')
        if 'agent_id' in request.data:
            defaults['agent_id'] = request.data.get('agent_id')
        if 'app_id' in request.data:
            defaults['app_id'] = request.data.get('app_id')
        if 'app_secret' in request.data and request.data.get('app_secret'):
            defaults['app_secret'] = request.data.get('app_secret')
        
        # OAuth settings
        if 'oauth_enabled' in request.data:
            defaults['oauth_enabled'] = request.data.get('oauth_enabled', True)
        if 'callback_url' in request.data:
            defaults['callback_url'] = request.data.get('callback_url')
        
        # Sync settings
        if 'sync_enabled' in request.data:
            defaults['sync_enabled'] = request.data.get('sync_enabled', True)
        if 'sync_departments' in request.data:
            defaults['sync_departments'] = request.data.get('sync_departments', True)
        if 'sync_users' in request.data:
            defaults['sync_users'] = request.data.get('sync_users', True)
        if 'sync_interval' in request.data:
            defaults['sync_interval'] = request.data.get('sync_interval', 60)
        if 'root_department_id' in request.data:
            defaults['root_department_id'] = request.data.get('root_department_id')
        
        # User creation settings
        if 'auto_create_user' in request.data:
            defaults['auto_create_user'] = request.data.get('auto_create_user', True)
        if 'auto_create_department' in request.data:
            defaults['auto_create_department'] = request.data.get('auto_create_department', True)
        if 'default_role_id' in request.data:
            defaults['default_role_id'] = request.data.get('default_role_id')
        
        config, created = SSOConfig.objects.update_or_create(
            company=company,
            provider=provider,
            defaults=defaults
        )
        
        return Response({
            'message': '配置保存成功',
            'id': config.id,
            'created': created
        })


class SSOConfigDetailView(APIView):
    """SSO配置详情 - 更新单个配置"""
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return SSOConfig.objects.get(pk=pk)
        except SSOConfig.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """获取单个SSO配置"""
        config = self.get_object(pk)
        if not config:
            return Response({'msg': '配置不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'id': config.id,
            'company': config.company_id,
            'company_name': config.company.name if config.company else None,
            'provider': config.provider,
            'provider_display': config.get_provider_display(),
            'corp_id': config.corp_id,
            'agent_id': config.agent_id,
            'app_id': config.app_id,
            'oauth_enabled': config.oauth_enabled,
            'callback_url': config.callback_url,
            'sync_enabled': config.sync_enabled,
            'sync_departments': config.sync_departments,
            'sync_users': config.sync_users,
            'sync_interval': config.sync_interval,
            'root_department_id': config.root_department_id,
            'auto_create_user': config.auto_create_user,
            'auto_create_department': config.auto_create_department,
            'default_role_id': config.default_role_id,
            'is_enabled': config.is_enabled,
            'auto_sync': config.auto_sync,
            'extra_config': config.extra_config,
            'last_sync_at': config.last_sync_at,
            'created_at': config.created_at,
            'updated_at': config.updated_at
        })
    
    def patch(self, request, pk):
        """更新SSO配置"""
        config = self.get_object(pk)
        if not config:
            return Response({'msg': '配置不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # Update fields if provided
        if 'is_enabled' in request.data:
            config.is_enabled = request.data.get('is_enabled')
        if 'auto_sync' in request.data:
            config.auto_sync = request.data.get('auto_sync')
        if 'extra_config' in request.data:
            config.extra_config = request.data.get('extra_config')
        
        # Core credentials
        if 'corp_id' in request.data:
            config.corp_id = request.data.get('corp_id')
        if 'agent_id' in request.data:
            config.agent_id = request.data.get('agent_id')
        if 'app_id' in request.data:
            config.app_id = request.data.get('app_id')
        if 'app_secret' in request.data and request.data.get('app_secret'):
            config.app_secret = request.data.get('app_secret')
        
        # OAuth settings
        if 'oauth_enabled' in request.data:
            config.oauth_enabled = request.data.get('oauth_enabled')
        if 'callback_url' in request.data:
            config.callback_url = request.data.get('callback_url')
        
        # Sync settings
        if 'sync_enabled' in request.data:
            config.sync_enabled = request.data.get('sync_enabled')
        if 'sync_departments' in request.data:
            config.sync_departments = request.data.get('sync_departments')
        if 'sync_users' in request.data:
            config.sync_users = request.data.get('sync_users')
        if 'sync_interval' in request.data:
            config.sync_interval = request.data.get('sync_interval')
        if 'root_department_id' in request.data:
            config.root_department_id = request.data.get('root_department_id')
        
        # User creation settings
        if 'auto_create_user' in request.data:
            config.auto_create_user = request.data.get('auto_create_user')
        if 'auto_create_department' in request.data:
            config.auto_create_department = request.data.get('auto_create_department')
        if 'default_role_id' in request.data:
            config.default_role_id = request.data.get('default_role_id')
        
        config.save()
        
        return Response({
            'message': '配置更新成功',
            'id': config.id
        })
    
    def delete(self, request, pk):
        """删除SSO配置"""
        config = self.get_object(pk)
        if not config:
            return Response({'msg': '配置不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        config.delete()
        return Response({'message': '配置已删除'})


class SSOTestConnectionView(APIView):
    """测试SSO连接"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        provider = request.data.get('provider')
        app_id = request.data.get('app_id')
        app_secret = request.data.get('app_secret')
        
        try:
            # 创建临时配置进行测试
            class TempConfig:
                def __init__(self):
                    self.app_id = app_id
                    self.app_secret = app_secret
                    self.extra_config = request.data.get('extra_config', {})
                    self.company = None
            
            temp_config = TempConfig()
            
            if provider == 'wework':
                service = WeWorkService(temp_config)
                access_token = service.get_access_token()
            elif provider == 'dingtalk':
                service = DingTalkService(temp_config)
                access_token = service.get_access_token()
            elif provider == 'feishu':
                service = FeishuService(temp_config)
                access_token = service.get_access_token()
            else:
                return Response({'error': '不支持的平台'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'success': True,
                'message': '连接测试成功'
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'连接测试失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class SSOSyncLogView(APIView):
    """SSO同步日志"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取同步日志列表"""
        provider = request.query_params.get('provider')
        limit = int(request.query_params.get('limit', 20))
        
        queryset = SSOSyncLog.objects.select_related('sso_config').order_by('-started_at')
        
        if provider:
            queryset = queryset.filter(sso_config__provider=provider)
        
        logs = []
        for log in queryset[:limit]:
            logs.append({
                'id': log.id,
                'provider': log.sso_config.provider,
                'provider_display': log.sso_config.get_provider_display(),
                'sync_type': log.sync_type,
                'sync_type_display': log.get_sync_type_display(),
                'status': log.status,
                'status_display': log.get_status_display(),
                'total_count': log.total_count,
                'success_count': log.success_count,
                'failed_count': log.failed_count,
                'error_message': log.error_message,
                'detail': log.detail,
                'started_at': log.started_at,
                'completed_at': log.completed_at
            })
        
        return Response(logs)


class SSOStatsView(APIView):
    """SSO统计信息"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取同步统计"""
        total_users = User.objects.filter(sso_bindings__isnull=False).distinct().count()
        
        # 统计有SSO关联的部门
        from django.db.models import Q
        total_depts = Department.objects.filter(
            Q(wework_dept_id__isnull=False) |
            Q(dingtalk_dept_id__isnull=False) |
            Q(feishu_dept_id__isnull=False)
        ).count()
        
        # 统计有负责人的部门
        total_managers = Department.objects.filter(manager__isnull=False).count()
        
        # 获取最近一次成功同步
        last_sync = SSOSyncLog.objects.filter(status='success').order_by('-completed_at').first()
        
        # 获取启用的SSO源
        enabled_configs = SSOConfig.objects.filter(is_enabled=True)
        sync_sources = [c.get_provider_display() for c in enabled_configs]
        
        return Response({
            'total_users': total_users,
            'total_depts': total_depts,
            'total_managers': total_managers,
            'last_sync_time': last_sync.completed_at if last_sync else None,
            'sync_sources': sync_sources,
            'sync_source': sync_sources[0] if sync_sources else '未配置'
        })
