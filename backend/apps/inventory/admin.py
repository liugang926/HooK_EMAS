from django.contrib import admin
from .models import InventoryTask, InventoryRecord


class InventoryRecordInline(admin.TabularInline):
    model = InventoryRecord
    extra = 0
    readonly_fields = ['asset', 'result', 'remark']


@admin.register(InventoryTask)
class InventoryTaskAdmin(admin.ModelAdmin):
    list_display = ['task_no', 'name', 'status', 'start_date', 'end_date', 'company']
    list_filter = ['status', 'start_date']
    search_fields = ['task_no', 'name']
    inlines = [InventoryRecordInline]


@admin.register(InventoryRecord)
class InventoryRecordAdmin(admin.ModelAdmin):
    list_display = ['task', 'asset', 'result', 'remark']
    list_filter = ['result', 'task']
    search_fields = ['asset__name', 'asset__asset_code']
