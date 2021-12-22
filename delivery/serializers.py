from rest_framework import serializers
from .models import DesignatedParcel


class DesignatedParcelSerializer(serializers.ModelSerializer):
    user_detail = serializers.ReadOnlyField()
    
    class Meta:
        model = DesignatedParcel
        fields = '__all__'
