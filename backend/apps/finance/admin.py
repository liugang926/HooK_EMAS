from django.contrib import admin
from .models import DepreciationScheme, DepreciationRecord, AssetLedger, AssetAccounting


@admin.register(DepreciationScheme)
class DepreciationSchemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'method', 'useful_life', 'salvage_rate', 'is_active', 'company']
    list_filter = ['method', 'is_active', 'company']
    search_fields = ['name']


@admin.register(DepreciationRecord)
class DepreciationRecordAdmin(admin.ModelAdmin):
    list_display = ['asset', 'period', 'depreciation_amount', 'accumulated_depreciation', 'current_value']
    list_filter = ['period']
    search_fields = ['asset__name', 'asset__asset_code']


@admin.register(AssetLedger)
class AssetLedgerAdmin(admin.ModelAdmin):
    list_display = ['asset', 'original_value', 'accumulated_depreciation', 'current_value']
    search_fields = ['asset__name', 'asset__asset_code']


@admin.register(AssetAccounting)
class AssetAccountingAdmin(admin.ModelAdmin):
    list_display = ['accounting_no', 'accounting_date', 'total_amount', 'status', 'created_by']
    list_filter = ['status', 'accounting_date']
    search_fields = ['accounting_no']
