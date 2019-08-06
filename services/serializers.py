from rest_framework import serializers
from inventory.serializers import InventoryItemSerializer

from . import models


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = models.Service


class ServicePersonSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["name", "id" ]
        model = models.ServicePerson

class ServiceTeamSerializer(serializers.ModelSerializer):
    members = ServicePersonSerializer(many=True)
    class Meta:
        fields = "__all__"
        model = models.ServiceTeam


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['description']
        model = models.Task


class ProcedureSerializer(serializers.ModelSerializer):
    steps = TaskSerializer(many=True)
    required_equipment = InventoryItemSerializer(many=True)
    required_consumables = InventoryItemSerializer(many=True)

    class Meta:
        fields = ['required_equipment', 'required_consumables', 'steps']
        model = models.ServiceProcedure


class WorkOrderSerializer(serializers.ModelSerializer):
    service_people = ServicePersonSerializer(many=True)
    class Meta:
        fields = ['service_people', 'id']
        model = models.ServiceWorkOrder
