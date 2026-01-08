from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API 路由
    path('api/auth/', include('apps.accounts.urls')),
    path('api/organizations/', include('apps.organizations.urls')),
    path('api/assets/', include('apps.assets.urls')),
    path('api/consumables/', include('apps.consumables.urls')),
    path('api/procurement/', include('apps.procurement.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/workflows/', include('apps.workflows.urls')),
    path('api/sso/', include('apps.sso.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/system/', include('apps.system.urls')),
]

# 开发环境下的媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
