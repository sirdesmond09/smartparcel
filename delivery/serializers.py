from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import DesignatedParcel


class DesignatedParcelSerializer(serializers.ModelSerializer):
    user_detail = serializers.ReadOnlyField()
    sender_detail = serializers.ReadOnlyField()
    parcel_pickup = serializers.ReadOnlyField()
    box_address  = serializers.ReadOnlyField()
    class Meta:
        model = DesignatedParcel
        fields = ['id','delivery_user','parcel', 'status', 'is_active', 'user_detail', 'sender_detail', 'parcel_pickup', 'box_address', 'date_assigned' ]
        
        

class VerifyDeliveryCodeSerializer(serializers.Serializer):
    delivery_code = serializers.CharField(max_length=6)
    
    
    def verify_code(self, designated_parcel):
        if self.validated_data['delivery_code'] == designated_parcel.delivery_code:
            if designated_parcel.status != 'completed':
                designated_parcel.status = "completed"
                designated_parcel.save()
                
                
                designated_parcel.parcel.status == 'completed'
                designated_parcel.parcel.save()
                
                return True
            else:
                raise ValidationError(detail="This code has been used for this parcel before.")
        else:
            raise ValidationError(detail="Incorrect Delivery Code")
            
