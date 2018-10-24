from rest_framework import serializers

from . import models


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tax
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = "__all__"

        
class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Expense
        fields = "__all__"
