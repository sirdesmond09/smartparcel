from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import BoxLocation, Parcel, Payments
from main.helpers.vonagesms import send_sms
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
class SelfStorageSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=400)
    duration = serializers.CharField(max_length=300)
    location = serializers.IntegerField()
    description = serializers.CharField(max_length=5000, required=False, allow_blank = True)
    
    
        

class CustomerToCusomterSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=400)
    name = serializers.CharField(max_length=400)
    phone = serializers.CharField(max_length=400)
    email = serializers.EmailField()
    address = serializers.CharField(max_length=400)
    location = serializers.IntegerField()
    description = serializers.CharField(max_length=5000, required=False, allow_blank = True)
    
        
class CustomerToCourierSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=400)
    name = serializers.CharField(max_length=400)
    phone = serializers.CharField(max_length=400)
    email = serializers.EmailField()
    address = serializers.CharField(max_length=400)
    location = serializers.IntegerField()   
    city = serializers.CharField(max_length=400) 
    description = serializers.CharField(max_length=5000, required=False, allow_blank = True)

class PaymentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Payments
        fields = '__all__'
        depth = 1
        
        
class ParcelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Parcel
        fields = '__all__'
        depth=1
        
        
class VerifySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code_used = serializers.CharField(max_length=200)
    
    
    def change_status(self):
        try:
            parcel = Parcel.objects.get(id=self.validated_data['id'], is_active=True)
        except Parcel.DoesNotExist:
            raise ValidationError(detail="Parcel not found")
        if self.validated_data['code_used'] == 'pick_up':
            parcel.pickup_used = True
            parcel.status = 'completed'
            parcel.save()
            
            parcel.location.available_space+=1
            parcel.location.save()
            # TODO : send email and sms notice
            return True
            
            
        elif self.validated_data['code_used'] == 'drop_off':
            parcel.dropoff_used = True
            parcel.status = 'dropped'
            parcel.save()
            send_sms(reason='drop_off', code=parcel.pick_up,phone=parcel.phone, address=parcel.address)
            # TODO : send email 
            return True
        
        return False
    
            
            
class UpdateLocationSerializer(serializers.Serializer):
    location = serializers.CharField()
    
    