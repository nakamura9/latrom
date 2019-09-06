from rest_framework import serializers

from . import models


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tax
        fields = '__all__'

class AccountingSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AccountingSettings
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = "__all__"

        
class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Expense
        fields = "__all__"

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = "__all__"


class CurrencyConversionLineSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(many=False)
    
    class Meta:
        model = models.CurrencyConversionLine
        fields = "__all__"

    def create(self, validated_data):
        curr = models.Currency.objects.create(
            **validated_data['currency']
        )
        line = models.CurrencyConversionLine.objects.create(
            currency=curr,
            exchange_rate=validated_data['exchange_rate'],
            conversion_table=validated_data['conversion_table']
        )
        return line

class CurrencyConversionTableSerializer(serializers.ModelSerializer):
    reference_currency = CurrencySerializer(many=False, read_only=False)
    currencyconversionline_set = CurrencyConversionLineSerializer(many=True, read_only=True)

    class Meta:
        model = models.CurrencyConversionTable
        fields = "__all__"
        validators = []

    def create(self, validated_data):
        
        table = models.CurrencyConversionTable.objects.create(
            reference_currency = validated_data['reference_currency'],
            name = validated_data['name']
        )
        return table
