from django.template.loader import render_to_string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import ResetPasswordOTP, User
from django.contrib.auth import password_validation
import pyotp

forgot_totp = pyotp.TOTP('72BPRLF7WDZTG46LL5MQAQVFK4WBGS3S', interval=300)

class UserSerializer(serializers.ModelSerializer):
    self_storages = serializers.ReadOnlyField()
    customer_to_customer = serializers.ReadOnlyField()
    payment_history = serializers.ReadOnlyField()
    customer_to_courier = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'email', 'phone', 'role','password', 'address','profile_pics', 'profile_pics_url','date_joined', 'self_storages', 'customer_to_customer', 'customer_to_courier','payment_history']
        
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
            
class ChangeRoleSerializer(serializers.Serializer):
    role = serializers.CharField()
    
    


# class CookieTokenRefreshSerializer(TokenRefreshSerializer):
#     refresh = None
#     def validate(self, attrs):
#         attrs['refresh'] = self.context['request'].COOKIES.get('refresh')
#         if attrs['refresh']:
#             return super().validate(attrs)
#         else:
#             raise InvalidToken('No valid token found in cookie \'refresh_token\'')

  
class ResetPasswordOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
     
    def get_otp(self):
        try:
            user = User.objects.get(email=self.validated_data['email'], is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError(detail='There is no active user with this email')
        
        code = forgot_totp.now()

        ResetPasswordOTP.objects.create(code=code, email=self.validated_data['email'], user=user)
        
        return {'message': 'Please check your email for OTP.'}
        
        
        
class ConfirmResetOtpSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    email = serializers.EmailField()

    def verify_otp(self):
        code = self.validated_data['otp']
        email = self.validated_data['email']
        
        if ResetPasswordOTP.objects.filter(code=code, email=email).exists():
            try:
                otp = ResetPasswordOTP.objects.get(code=code, email=email)
            except Exception:
                ResetPasswordOTP.objects.filter(code=code, email=email).delete()
                raise serializers.ValidationError(detail='Cannot verify otp. Please try later')
            
            if forgot_totp.verify(otp.code):
                    
                return {'message': 'success'}
            
            else:
                raise serializers.ValidationError(detail='OTP Expired or Invalid')   
            
            
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=300) 
    
    def reset_password(self):
        try:
            user = User.objects.get(email=self.validated_data['email'], is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError(detail='Error Changing Password')
        
        user.set_password(self.validated_data['password'])
        user.save()
        
        return {'message': 'Password reset complete'}