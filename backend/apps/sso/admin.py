from django.contrib import admin
from .models import SSOConfig, SSOUserBinding


@admin.register(SSOConfig)
class SSOConfigAdmin(admin.ModelAdmin):
    list_display = ['company', 'provider', 'is_enabled', 'updated_at']
    list_filter = ['provider', 'is_enabled']
    search_fields = ['company__name']


@admin.register(SSOUserBinding)
class SSOUserBindingAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'provider_user_id', 'created_at']
    list_filter = ['provider', 'created_at']
    search_fields = ['user__username', 'provider_user_id']
