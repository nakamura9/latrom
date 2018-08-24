from rest_framework import serializers
from . import models
from inventory.serializers import SupplierSerializer
from invoicing.serializers import CustomerSerializer
from employees.serializers import EmployeeSerializer

class EventParticipantSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(many=False)
    supplier = SupplierSerializer(many=False)
    customer = CustomerSerializer(many=False)
    class Meta:
        model = models.EventParticipant
        fields = "__all__"

class EventSerializer(serializers.ModelSerializer):
    participants = EventParticipantSerializer(many=True)
    class Meta:
        model = models.Event
        fields = "__all__"