from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from django.utils import timezone

from .models import Notification, NotificationRecipient, Announcement, AlertRule


class NotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = '__all__'
    
    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            record = NotificationRecipient.objects.filter(
                notification=obj, user=request.user
            ).first()
            return record.is_read if record else False
        return False


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'


class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = '__all__'


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notification_type', 'company']
    
    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(
            recipient_records__user=user
        ).distinct()
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读消息数量"""
        count = NotificationRecipient.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'count': count})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """标记为已读"""
        notification = self.get_object()
        record, created = NotificationRecipient.objects.get_or_create(
            notification=notification,
            user=request.user,
            defaults={'is_read': True, 'read_at': timezone.now()}
        )
        if not created:
            record.is_read = True
            record.read_at = timezone.now()
            record.save()
        return Response({'message': '已标记为已读'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """全部标记为已读"""
        NotificationRecipient.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({'message': '全部已标记为已读'})


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.filter(is_published=True)
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company', 'is_top']


class AlertRuleViewSet(viewsets.ModelViewSet):
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company', 'alert_type', 'is_active']
