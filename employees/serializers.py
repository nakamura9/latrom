from rest_framework import serializers

from . import models


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Employee
        fields = '__all__'

class PayslipSerializer(serializers.ModelSerializer):
    gross = serializers.SerializerMethodField()
    deductions = serializers.SerializerMethodField()
    taxes = serializers.SerializerMethodField()
    employee = EmployeeSerializer(many=False)
    
    class Meta:
        model = models.Payslip
        fields = "__all__"

    def get_gross(self, obj):
        return obj.gross_pay

    def get_deductions(self, obj):
        return obj.non_tax_deductions

    def get_taxes(self, obj):
        return obj.total_payroll_taxes

class AttendanceLineSerializer(serializers.ModelSerializer):
    working_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = models.AttendanceLine
        fields = '__all__'

    def get_working_hours(self, obj):
        return str(obj.working_time)

class TimeSheetSerializer(serializers.ModelSerializer):
    attendanceline_set = AttendanceLineSerializer(many=True)
    class Meta:
        model = models.EmployeeTimeSheet
        fields = '__all__'

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class DepartmentSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True)
    class Meta:
        model = models.Department
        fields = "__all__"
