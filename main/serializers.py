from rest_framework import serializers
from .models import BoxLocation, CustomerToCustomer, SelfStorage

class BoxLocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BoxLocation
        fields = '__all__'
        
        
class SelfStorageSerializer(serializers.ModelSerializer):
    reference = serializers.CharField(max_length=400, write_only=True)
    address = serializers.ReadOnlyField()
    class Meta:
        model = SelfStorage
        fields = '__all__'
        

class CustomerToCusomterSerializer(serializers.ModelSerializer):
    reference = serializers.CharField(max_length=400, write_only=True)
    address = serializers.ReadOnlyField()
    class Meta:
        model = CustomerToCustomer
        fields = '__all__'