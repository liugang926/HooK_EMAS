from rest_framework import serializers
from .models import WorkflowTemplate, WorkflowNode, WorkflowInstance, WorkflowTask


class WorkflowNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowNode
        fields = '__all__'


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    nodes = WorkflowNodeSerializer(many=True, read_only=True)
    
    class Meta:
        model = WorkflowTemplate
        fields = '__all__'


class WorkflowTaskSerializer(serializers.ModelSerializer):
    assignee_name = serializers.CharField(source='assignee.display_name', read_only=True)
    node_name = serializers.CharField(source='node.name', read_only=True)
    
    class Meta:
        model = WorkflowTask
        fields = '__all__'


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    initiator_name = serializers.CharField(source='initiator.display_name', read_only=True)
    tasks = WorkflowTaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = WorkflowInstance
        fields = '__all__'
