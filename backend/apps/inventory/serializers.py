from rest_framework import serializers
from .models import InventoryTask, InventoryRecord


class InventoryTaskSerializer(serializers.ModelSerializer):
    executor_name = serializers.CharField(source='executor.display_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryTask
        fields = '__all__'
    
    def get_progress(self, obj):
        total = obj.records.count()
        if total == 0:
            return 0
        completed = obj.records.filter(status='completed').count()
        return int(completed / total * 100)


class InventoryRecordSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    
    class Meta:
        model = InventoryRecord
        fields = '__all__'
