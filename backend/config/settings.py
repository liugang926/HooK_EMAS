"""
Django 配置文件 - 精臣云资产管理系统
"""
import os
from pathlib import Path
from datetime import timedelta
import dj_database_url

# 基础路径
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全密钥
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

# 调试模式
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# 允许的主机
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# 应用定义
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 第三方应用
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'django_celery_beat',
    'django_celery_results',
    'import_export',
    'mptt',
    
    # 本地应用
    'apps.common',  # 通用基类和工具
    'apps.accounts',
    'apps.organizations',
    'apps.assets',
    'apps.consumables',
    'apps.procurement',
    'apps.inventory',
    'apps.finance',
    'apps.reports',
    'apps.workflows',
    'apps.sso',
    'apps.notifications',
    'apps.system',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.system.logging.OperationLogMiddleware',  # 操作日志中间件
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# 数据库配置
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgres://asset_user:asset_password_2024@localhost:5432/asset_management'
)
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL)
}

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 自定义用户模型
AUTH_USER_MODEL = 'accounts.User'

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# 媒体文件
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 默认主键类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # 统一异常处理（遵循 .cursorrules 规约）
    'EXCEPTION_HANDLER': 'apps.common.exceptions.unified_exception_handler',
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
}

# JWT 配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# CORS 配置
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
CORS_ALLOW_CREDENTIALS = True

# API 文档配置
SPECTACULAR_SETTINGS = {
    'TITLE': '精臣云资产管理系统 API',
    'DESCRIPTION': '企业固定资产管理系统 REST API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Redis 配置
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session 配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Celery 配置
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# 文件上传配置
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# SSO 配置
# 企业微信
WEWORK_CORP_ID = os.environ.get('WEWORK_CORP_ID', '')
WEWORK_AGENT_ID = os.environ.get('WEWORK_AGENT_ID', '')
WEWORK_SECRET = os.environ.get('WEWORK_SECRET', '')
WEWORK_CALLBACK_URL = os.environ.get('WEWORK_CALLBACK_URL', 'http://localhost:8000/api/sso/wework/callback/')

# 钉钉
DINGTALK_APP_KEY = os.environ.get('DINGTALK_APP_KEY', '')
DINGTALK_APP_SECRET = os.environ.get('DINGTALK_APP_SECRET', '')
DINGTALK_CALLBACK_URL = os.environ.get('DINGTALK_CALLBACK_URL', 'http://localhost:8000/api/sso/dingtalk/callback/')

# 飞书
FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID', '')
FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET', '')
FEISHU_CALLBACK_URL = os.environ.get('FEISHU_CALLBACK_URL', 'http://localhost:8000/api/sso/feishu/callback/')

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# 确保日志目录存在
(BASE_DIR / 'logs').mkdir(exist_ok=True)
