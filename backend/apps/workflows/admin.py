from django.contrib import admin
from .models import WorkflowTemplate, WorkflowNode, WorkflowInstance, WorkflowTask


class WorkflowNodeInline(admin.TabularInline):
    model = WorkflowNode
    extra = 1


@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'business_type', 'is_active', 'company']
    list_filter = ['business_type', 'is_active']
    search_fields = ['name']
    inlines = [WorkflowNodeInline]


class WorkflowTaskInline(admin.TabularInline):
    model = WorkflowTask
    extra = 0
    readonly_fields = ['node', 'assignee', 'status', 'comment', 'completed_at']


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ['template', 'initiator', 'status', 'created_at']
    list_filter = ['status', 'template']
    search_fields = ['initiator__username']
    inlines = [WorkflowTaskInline]


@admin.register(WorkflowTask)
class WorkflowTaskAdmin(admin.ModelAdmin):
    list_display = ['instance', 'node', 'assignee', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['instance__initiator__username', 'assignee__username']
