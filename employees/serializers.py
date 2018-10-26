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

class AttendanceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AttendanceLine
        fields = '__all__'

class TimeSheetSerializer(serializers.ModelSerializer):
    attendanceline_set = AttendanceLineSerializer(many=True)
    class Meta:
        model = models.EmployeeTimeSheet
        fields = '__all__'