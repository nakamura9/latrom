from rest_framework import serializers
from manufacturing import models 

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Shift
        fields = "__all__"