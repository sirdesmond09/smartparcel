from rest_framework import serializers
from .models import DesignatedParcel


class DesignatedParcelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DesignatedParcel
        fields = '__all__'
        depth =1
