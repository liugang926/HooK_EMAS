"""
操作日志记录工具
"""
from functools import wraps
from django.utils import timezone


def get_client_ip(request):
    """获取客户端 IP 地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def log_operation(module, action, content_template=None):
    """
    操作日志装饰器
    
    用法:
    @log_operation('asset', 'create', '新增资产 {name}')
    def create(self, request, *args, **kwargs):
        ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            response = func(self, request, *args, **kwargs)
            
            # 只记录成功的操作
            if response.status_code in [200, 201, 204]:
                try:
                    from .models import OperationLog
                    
                    # 生成内容
                    content = content_template or f'{action} 操作'
                    if hasattr(response, 'data') and response.data:
                        # 尝试格式化内容
                        try:
                            data = response.data
                            if isinstance(data, dict):
                                content = content_template.format(**data) if content_template else str(data.get('name', action))
                        except (KeyError, TypeError):
                            pass
                    
                    # 获取公司 ID
                    company_id = None
                    if hasattr(request, 'company_id'):
                        company_id = request.company_id
                    elif hasattr(self, 'get_queryset'):
                        # 尝试从 queryset 获取公司
                        qs = self.get_queryset()
                        if qs.exists() and hasattr(qs.first(), 'company_id'):
                            company_id = qs.first().company_id
                    
                    OperationLog.objects.create(
                        company_id=company_id,
                        module=module,
                        action=action,
                        content=content,
                        operator=request.user if request.user.is_authenticated else None,
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                    )
                except Exception as e:
                    # 日志记录失败不影响主业务
                    print(f"记录操作日志失败: {e}")
            
            return response
        return wrapper
    return decorator


def record_log(request, module, action, content, company_id=None):
    """
    手动记录操作日志
    
    用法:
    record_log(request, 'system', 'login', '用户登录系统')
    """
    try:
        from .models import OperationLog
        
        OperationLog.objects.create(
            company_id=company_id,
            module=module,
            action=action,
            content=content,
            operator=request.user if request.user.is_authenticated else None,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
    except Exception as e:
        print(f"记录操作日志失败: {e}")


class OperationLogMiddleware:
    """
    操作日志中间件
    自动记录登录、登出等操作
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # 需要记录的 URL 模式
        self.log_patterns = {
            '/api/accounts/login/': ('system', 'login', '用户登录系统'),
            '/api/accounts/logout/': ('system', 'logout', '用户登出系统'),
        }
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # 检查是否需要记录
        path = request.path
        if path in self.log_patterns and response.status_code in [200, 201]:
            module, action, content = self.log_patterns[path]
            
            # 获取用户
            user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            
            try:
                from .models import OperationLog
                
                OperationLog.objects.create(
                    module=module,
                    action=action,
                    content=content,
                    operator=user,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )
            except Exception as e:
                print(f"记录操作日志失败: {e}")
        
        return response
