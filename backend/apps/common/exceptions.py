"""
统一异常处理 - 精臣云资产管理系统

遵循 .cursorrules 规约:
后端异常必须捕获并返回统一格式的 JSON：{"code": 400, "msg": "错误信息", "data": null}
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError
import logging

logger = logging.getLogger(__name__)


class BusinessException(Exception):
    """
    业务异常基类
    
    用于业务逻辑中主动抛出的异常
    """
    
    def __init__(self, msg: str, code: int = 400, data=None):
        self.msg = msg
        self.code = code
        self.data = data
        super().__init__(msg)


class NotFoundError(BusinessException):
    """资源不存在异常"""
    
    def __init__(self, msg: str = '资源不存在', data=None):
        super().__init__(msg=msg, code=404, data=data)


class ValidationError(BusinessException):
    """验证异常"""
    
    def __init__(self, msg: str = '数据验证失败', data=None):
        super().__init__(msg=msg, code=400, data=data)


class PermissionError(BusinessException):
    """权限异常"""
    
    def __init__(self, msg: str = '没有操作权限', data=None):
        super().__init__(msg=msg, code=403, data=data)


def unified_exception_handler(exc, context):
    """
    统一异常处理器
    
    遵循 .cursorrules 规约:
    后端异常必须捕获并返回统一格式的 JSON：{"code": 400, "msg": "错误信息", "data": null}
    
    Args:
        exc: 异常对象
        context: 上下文信息
        
    Returns:
        统一格式的 Response
    """
    # 先调用 DRF 默认的异常处理
    response = exception_handler(exc, context)
    
    # 记录异常日志
    view = context.get('view', None)
    view_name = view.__class__.__name__ if view else 'Unknown'
    logger.error(f"[{view_name}] Exception: {str(exc)}", exc_info=True)
    
    # 处理业务异常
    if isinstance(exc, BusinessException):
        return Response({
            'code': exc.code,
            'msg': exc.msg,
            'data': exc.data
        }, status=exc.code if 200 <= exc.code < 600 else 400)
    
    # 处理 404 异常
    if isinstance(exc, Http404):
        return Response({
            'code': 404,
            'msg': '资源不存在',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)
    
    # 处理权限异常
    if isinstance(exc, PermissionDenied):
        return Response({
            'code': 403,
            'msg': '没有操作权限',
            'data': None
        }, status=status.HTTP_403_FORBIDDEN)
    
    # 处理 DRF 异常
    if response is not None:
        # 提取错误信息
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                # 字段验证错误
                errors = []
                for field, messages in exc.detail.items():
                    if isinstance(messages, list):
                        for msg in messages:
                            errors.append(f'{field}: {msg}')
                    else:
                        errors.append(f'{field}: {messages}')
                msg = '; '.join(errors) if errors else '请求错误'
            elif isinstance(exc.detail, list):
                msg = '; '.join([str(e) for e in exc.detail])
            else:
                msg = str(exc.detail)
        else:
            msg = '请求错误'
        
        return Response({
            'code': response.status_code,
            'msg': msg,
            'data': None
        }, status=response.status_code)
    
    # 处理未知异常
    logger.exception(f"Unhandled exception: {str(exc)}")
    return Response({
        'code': 500,
        'msg': '服务器内部错误',
        'data': None
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 成功响应工具函数
def success_response(data=None, msg: str = '操作成功', code: int = 200):
    """
    统一成功响应
    
    Args:
        data: 响应数据
        msg: 成功消息
        code: 状态码
        
    Returns:
        Response 对象
    """
    return Response({
        'code': code,
        'msg': msg,
        'data': data
    }, status=code)


def error_response(msg: str = '操作失败', code: int = 400, data=None):
    """
    统一错误响应
    
    Args:
        msg: 错误消息
        code: 状态码
        data: 附加数据
        
    Returns:
        Response 对象
    """
    return Response({
        'code': code,
        'msg': msg,
        'data': data
    }, status=code)
