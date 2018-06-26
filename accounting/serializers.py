from rest_framework import serializers
import models 

class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tax
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Employee
        fields = '__all__'

class PayslipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Payslip
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = "__all__"

        