from account.serializers import UserSerializer
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
import pyotp
from .models import OTP
from config import settings
from rest_framework import serializers
from django.template.loader import render_to_string

totp = pyotp.TOTP('base32secret3232', interval=120)

domain = 'smartparcel.com'
url='#'
User = get_user_model()

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    token = "https://{}/forgot-password/{}".format(domain,reset_password_token.key)
    
    msg_html = render_to_string('forgot_password.html', {
                        'first_name': str(reset_password_token.user.first_name).title(),
                        'token':token})
    
    message= 'Hello {},\n\nYou are receiving this message because you or someone else have requested the reset of the password for your account.\nPlease click on the following link, or paste this into your browser to complete the process within 24hours of receiving it:\n{}\n\nPlease if you did not request this please ignore this e-mail and your password would remain unchanged.\n\nRegards,\nEDM Support'.format(reset_password_token.user.first_name, token)
    
    send_mail(
        subject = "RESET PASSWORD FOR SAMRT PARCEL",
        message= message,
        html_message=msg_html,
        from_email  = 'SMART PARCEL SUPPORT <noreply@smartparcel.com>',
        recipient_list= [reset_password_token.user.email]
    )
    
    
@receiver(post_save, sender=User)
def send_otp(sender, instance, created, **kwargs):
    if created:
        code = totp.now()
        print(code)
        subject = "ACCOUNT VERIFICATION FOR SMART PARCEL"
        
        message = f"""Hi, {str(instance.first_name).title()}.
Thank you for signing up!
Complete your verification on the smart parcel with the OTP below:

                {code}        

Expires in 60 seconds!

Thank you,
EDM Team                
"""   
        msg_html = render_to_string('signup_email.html', {
                        'first_name': str(instance.first_name).title(),
                        'code':code,
                        'url':url})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]
        send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
        
        OTP.objects.create(code=code, user=instance)
    
    

       
class OTPVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    
    
    def verify_otp(self):
        otp = self.validated_data['otp']
        
        if OTP.objects.filter(code=otp).exists():
            try:
                otp = OTP.objects.get(code=otp)
            except Exception:
                OTP.objects.filter(code=otp).delete()
                raise serializers.ValidationError(detail='Cannot verify otp. Please try later')
            
            if totp.verify(otp):
                if otp.user.is_active == False:
                    otp.user.is_active=True
                    otp.user.save()
                    
                    #clear all otp for this user after verification
                    all_otps = OTP.objects.filter(user=otp.user)
                    all_otps.delete()
                    
                    serializer = UserSerializer(otp.user)
                    return {'message': 'Verification Complete', 'data':serializer.data}
                else:
                    raise serializers.ValidationError(detail='User with this otp has been verified before.')
            
                
            else:
                raise serializers.ValidationError(detail='OTP expired')
                    
        
        else:
            raise serializers.ValidationError(detail='Invalid OTP')
        
        
class NewOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
     
    def get_new_otp(self):
        try:
            user = User.objects.get(email=self.validated_data['email'], is_active=False)
        except User.DoesNotExist:
            raise serializers.ValidationError(detail='Please confirm that the email is correct and has not been verified')
        
        code = totp.now()
        print(code)
        OTP.objects.create(code=code, user=user)
        subject = "NEW OTP FOR SMART PARCEL"
        
        message = f"""Hi, {str(user.first_name).title()}.

    Complete your verification on the smart parcel with the OTP below:

                    {code}        

    Expires in 60 seconds!

    Thank you,
    EDM Team                
    """
        msg_html = render_to_string('new_otp.html', {
                        'first_name': str(user.first_name).title(),
                        'code':code,
                        'url':url})
        
        email_from = settings.Common.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
        
        return {'message': 'Please check your email for OTP.'}
        
        
        
        