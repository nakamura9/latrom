from rest_framework import serializers
import models

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = models.Service