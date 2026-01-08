from django.urls import path
from . import views

urlpatterns = [
    # 企业微信
    path('wework/login/', views.WeWorkAuthView.as_view(), name='wework-login'),
    path('wework/callback/', views.WeWorkCallbackView.as_view(), name='wework-callback'),
    
    # 钉钉
    path('dingtalk/login/', views.DingTalkAuthView.as_view(), name='dingtalk-login'),
    path('dingtalk/callback/', views.DingTalkCallbackView.as_view(), name='dingtalk-callback'),
    
    # 飞书
    path('feishu/login/', views.FeishuAuthView.as_view(), name='feishu-login'),
    path('feishu/callback/', views.FeishuCallbackView.as_view(), name='feishu-callback'),
    
    # SSO配置管理
    path('configs/', views.SSOConfigView.as_view(), name='sso-configs'),
    path('configs/<int:pk>/', views.SSOConfigDetailView.as_view(), name='sso-config-detail'),
    path('test-connection/', views.SSOTestConnectionView.as_view(), name='sso-test-connection'),
    
    # 组织同步
    path('sync-organization/', views.SyncOrganizationView.as_view(), name='sync-organization'),
    path('sync-logs/', views.SSOSyncLogView.as_view(), name='sso-sync-logs'),
    path('stats/', views.SSOStatsView.as_view(), name='sso-stats'),
]
