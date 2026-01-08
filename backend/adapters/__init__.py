"""
第三方系统适配器层 (Adapter Layer)

遵循 .cursorrules 规约:
- 所有第三方系统（企微、钉钉、飞书、ERP）的集成必须通过此目录下的统一接口实现
- 新增集成平台时，必须继承 BasePlatformAdapter 类
"""

from .base import BasePlatformAdapter
from .wework import WeWorkAdapter
from .dingtalk import DingTalkAdapter
from .feishu import FeishuAdapter

__all__ = [
    'BasePlatformAdapter',
    'WeWorkAdapter',
    'DingTalkAdapter',
    'FeishuAdapter',
]
