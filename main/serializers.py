from rest_framework import serializers
from .models import BoxLocation, CustomerToCustomer, SelfStorage

class BoxLocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BoxLocation
        fields = '__all__'
        
        
class SelfStorageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SelfStorage
        fields = '__all__'
        

class CustomerToCusomterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomerToCustomer
        fields = '__all__'