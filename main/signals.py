from firebase_admin import messaging
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Parcel


@receiver(post_save, sender=Parcel)
def send_push_notification(sender, instance:Parcel, created, *args, **kwargs):
    if created:
        firebase_key = instance.user.firebase_key
        
        
        if instance.parcel_type == "self_storage":
            
            body = "Your booking for self storage has been confrimed"
        elif instance.parcel_type == "customer_to_customer":
            body = "Your booking to be sent to a customer has been confrimed"
        elif instance.parcel_type == "customer_to_courier":
            body = "Your booking for parcel delivery has been confrimed"
        else:
            body=""
        
        message = messaging.Message(
            token=firebase_key,
            notification=messaging.Notification(
                title='Booking Confirmed',
                body=body,
                ),
            data={
                'message':body
                }
            )
        
        try:
            response = messaging.send(message)
        except Exception as e:
            print(e)
        
