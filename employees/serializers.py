from rest_framework import serializers

from . import models


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Employee
        fields = '__all__'

class PayslipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Payslip
        fields = "__all__"
