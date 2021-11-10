from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, OTP
from django.contrib.auth import password_validation


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'username','first_name', 'last_name', 'email', 'phone', 'is_admin', 'is_staff','password', 'profile_pics', 'profile_pics_url','date_joined',]
        
    def validate_password(self, value):
        try:
            password_validation.validate_password(value, self.instance)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value
        
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password  = serializers.CharField(max_length=200)
    new_password  = serializers.CharField(max_length=200)
    confirm_password  = serializers.CharField(max_length=200)
    
    
    def check_pass(self):
        """ checks if both passwords are the same """
        if self.validated_data['new_password'] != self.validated_data['confirm_password']:
            raise serializers.ValidationError({"error":"Please enter matching passwords"})
        return True
            
 


# class CookieTokenRefreshSerializer(TokenRefreshSerializer):
#     refresh = None
#     def validate(self, attrs):
#         attrs['refresh'] = self.context['request'].COOKIES.get('refresh')
#         if attrs['refresh']:
#             return super().validate(attrs)
#         else:
#             raise InvalidToken('No valid token found in cookie \'refresh_token\'')