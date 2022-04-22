from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from account.signals import User

from main.helpers.notification import send_notification
from .models import BoxLocation, Parcel, Payments, BoxSize, Category, Compartment
from main.helpers.vonagesms import send_sms
from main.helpers.compartment import increase_spaces

class AddCategorySerializer(serializers.Serializer):
    name=serializers.CharField(max_length=300)
    spaces=serializers.IntegerField()
    
    
    def create_category(self):
        data = self.validated_data
        category = Category.objects.create(**data)
        try:
            compartments = [Compartment(number = i+1, category=category) for i in range(data['spaces'])]
            
            Compartment.objects.bulk_create(compartments)
            return category
        except Exception as e:
            category.delete()
            raise ValidationError(detail='Unable to add category')
    
    
class CategorySerializer(serializers.ModelSerializer):
    box_spaces = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = ["id",'name', 'spaces', 'created_at','box_spaces' ]
        
class CompartmentSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Compartment
        fields = "__all__"
        
        
class BoxSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxSize
        fields = "__all__"
        
        
class CenterSerializer(serializers.Serializer):
    center_name=serializers.CharField(max_length=300)
    address=serializers.CharField(max_length=500)
    category=serializers.IntegerField()
    
    def validate_category(self, value):
        if Category.objects.filter(id=value).exists():
            value = Category.objects.get(id=value)
            return value
        raise ValidationError(detail="Category does not exist")
    
    
class AddLocationSerializer(serializers.Serializer):
    location = serializers.CharField(max_length=300)
    centers = CenterSerializer(many=True)
    
    
    def add_location(self, request):
        location = self.validated_data.pop('location')
        
        # request.user=User.objects.first()
        try:
            box_location = [BoxLocation(
                **center,
                location=location, 
                available_small_space=center['category'].compartments.filter(size__name="small").count(), 
                available_medium_space=center['category'].compartments.filter(size__name="medium").count(), 
                available_large_space=center['category'].compartments.filter(size__name="large").count(),
                available_xlarge_space=center['category'].compartments.filter(size__name="xlarge").count(),
                available_xxlarge_space=center['category'].compartments.filter(size__name="xxlarge").count(),   
                user=request.user
                ) 
                for center in self.validated_data['centers']]
                
            BoxLocation.objects.bulk_create(box_location)
            return True
        except Exception as e:
            raise ValidationError(detail='Unable to add locations')
        
class BoxLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxLocation
        fields = '__all__'  
          
class SelfStorageSerializer(serializers.Serializer):
    allow_save = serializers.BooleanField()
    reference = serializers.CharField(max_length=400)
    duration = serializers.CharField(max_length=300)
    location = serializers.IntegerField()
    description = serializers.CharField(max_length=5000, required=False, allow_blank = True)
    size = serializers.IntegerField()
    
    def validate_size(self, value):
        if BoxSize.objects.filter(id=value).exists():
            value = BoxSize.objects.get(id=value)
            return value
        raise ValidationError(detail="Boxsize does not exist")
    
    

class CustomerToCusomterSerializer(serializers.Serializer):
    allow_save = serializers.BooleanField()
    reference = serializers.CharField(max_length=400)
    name = serializers.CharField(max_length=400)
    phone = serializers.CharField(max_length=400)
    email = serializers.EmailField()
    address = serializers.CharField(max_length=400)
    location = serializers.IntegerField()
    description = serializers.CharField(max_length=5000, required=False, allow_blank = True)
    size = serializers.IntegerField()
    
    def validate_size(self, value):
        if BoxSize.objects.filter(id=value).exists():
            value = BoxSize.objects.get(id=value)
            return value
        raise ValidationError(detail="Boxsize does not exist")
    
        
class CustomerToCourierSerializer(serializers.Serializer):
    allow_save = serializers.BooleanField()
    reference = serializers.CharField(max_length=400)
    name = serializers.CharField(max_length=400)
    phone = serializers.CharField(max_length=400)
    email = serializers.EmailField()
    address = serializers.CharField(max_length=400)
    location = serializers.IntegerField()   
    city = serializers.CharField(max_length=400) 
    description = serializers.CharField(max_length=5000, required=False, allow_blank = True)
    size = serializers.IntegerField()
    
    def validate_size(self, value):
        if BoxSize.objects.filter(id=value).exists():
            value = BoxSize.objects.get(id=value)
            return value
        raise ValidationError(detail="Boxsize does not exist")
    
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
        
        
class DropCodeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    apikey = serializers.CharField(max_length=200)
    code = serializers.CharField(max_length=4)
    
    
    def change_status(self, center):
        try:
            parcel = Parcel.objects.get(location=center,drop_off=self.validated_data['code'], dropoff_used=False,is_active=True)
        except Parcel.DoesNotExist:
            raise ValidationError({
                                    "message": "failed",
                                    "errors": {
                                        "code": [
                                        "Parcel does not exist"
                                        ]
                                    }
                                }
                            )
            
            
        parcel.dropoff_used = True
        parcel.status = 'dropped'
        parcel.save()
        
        if parcel.parcel_type != "self_storage":
            # send_sms(reason='drop_off', code=parcel.pick_up,phone=parcel.phone, address=center.address)
            # TODO : send email 
            pass
        send_notification(notice_for="dropped", user=parcel.user)
        return parcel
    

class PickCodeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    apikey = serializers.CharField(max_length=200)
    code = serializers.CharField(max_length=4)
    
    
    def change_status(self, center):
        try:
            parcel = Parcel.objects.get(location=center,pick_up=self.validated_data['code'], pickup_used=False,dropoff_used=True,is_active=True)
        except Parcel.DoesNotExist:
            raise ValidationError({
                                    "message": "failed",
                                    "errors": {
                                        "code": [
                                        "Parcel does not exist"
                                        ]
                                    }
                                }
                            )
            
            
        parcel.pickup_used = True
        parcel.status = 'completed'
        parcel.save()
        
        increase_spaces(parcel.compartment.size, center)
        
        send_notification(notice_for="picked", user=parcel.user)
        # TODO : send email 
        return parcel
        
    
            
            
class UpdateLocationSerializer(serializers.Serializer):
    location = serializers.CharField()
    
    