from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import BoxLocation, CustomerToCustomer, Payments, SelfStorage

class CenterSerializer(serializers.Serializer):
    center_name=serializers.CharField(max_length=300)
    address=serializers.CharField(max_length=500)
    no_of_compartment=serializers.IntegerField()
    
    
class AddLocationSerializer(serializers.Serializer):
    location = serializers.CharField(max_length=300)
    centers = CenterSerializer(many=True)
    
    
    def add_location(self, request):
        location = self.validated_data.pop('location')
        try:
            box_location = []
            for center in self.validated_data['centers']:
                box_location.append(BoxLocation(**center, location=location, available_space=center['no_of_compartment'], user=request.user))
            BoxLocation.objects.bulk_create(box_location)
            return True
        except Exception as e:
            raise ValidationError(detail='Unable to add locations')
        
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
        
        
class PaymentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Payments
        fields = '__all__'
        depth = 1