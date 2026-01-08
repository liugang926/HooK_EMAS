from rest_framework import serializers
from .models import DepreciationScheme, DepreciationRecord


class DepreciationSchemeSerializer(serializers.ModelSerializer):
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    asset_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DepreciationScheme
        fields = '__all__'
    
    def get_asset_count(self, obj):
        return obj.assets.count() if hasattr(obj, 'assets') else 0


class DepreciationRecordSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    
    class Meta:
        model = DepreciationRecord
        fields = '__all__'
