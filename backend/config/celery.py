"""
Celery 配置 - 精臣云资产管理系统
"""
import os
from celery import Celery

# 设置 Django settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 创建 Celery 应用
app = Celery('asset_management')

# 从 Django settings 读取配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')
