from django.urls import path
from . import views

urlpatterns = [
    path('assets/summary/', views.AssetSummaryReportView.as_view(), name='asset-summary'),
    path('assets/trend/', views.AssetTrendReportView.as_view(), name='asset-trend'),
    path('assets/by-department/', views.DepartmentAssetReportView.as_view(), name='asset-by-department'),
    path('consumables/summary/', views.ConsumableSummaryReportView.as_view(), name='consumable-summary'),
]
