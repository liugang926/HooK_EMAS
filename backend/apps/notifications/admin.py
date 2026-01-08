from django.contrib import admin
from .models import Notification, NotificationRecipient, Announcement, AlertRule


class NotificationRecipientInline(admin.TabularInline):
    model = NotificationRecipient
    extra = 0


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'is_global', 'created_by', 'created_at']
    list_filter = ['notification_type', 'is_global', 'created_at']
    search_fields = ['title', 'content']
    inlines = [NotificationRecipientInline]


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_top', 'is_published', 'publish_time', 'created_by']
    list_filter = ['is_top', 'is_published']
    search_fields = ['title', 'content']


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'alert_type', 'advance_days', 'is_active', 'company']
    list_filter = ['alert_type', 'is_active']
    search_fields = ['name']
