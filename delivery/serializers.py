from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import DesignatedParcel


class DesignatedParcelSerializer(serializers.ModelSerializer):
    user_detail = serializers.ReadOnlyField()
    
    class Meta:
        model = DesignatedParcel
        fields = ['id','delivery_user','parcel', 'status','user_detail', 'is_active']
        
        

class VerifyDeliveryCodeSerializer(serializers.Serializer):
    delivery_code = serializers.CharField(max_length=6)
    
    
    def verify_code(self, designated_parcel):
        if self.validated_data['delivery_code'] == designated_parcel.delivery_code:
            if designated_parcel.status != 'completed':
                designated_parcel.status = "completed"
                designated_parcel.save()
                return True
            else:
                raise ValidationError(detail="This code has been used for this parcel before.")
        else:
            raise ValidationError(detail="Incorrect Delivery Code")
            
