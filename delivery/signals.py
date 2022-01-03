from firebase_admin import messaging
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import DesignatedParcel


@receiver(post_save, sender=DesignatedParcel)
def send_push_notification(sender, instance:DesignatedParcel, created, *args, **kwargs):
    if created:
        
        firebase_key = instance.delivery_user.firebase_key
        
        
        body = f"""Hello, {instance.user_detail['first_name']}
A new parcel has been assigned to you."""
        
        message = messaging.Message(
            token=firebase_key,
            notification=messaging.Notification(
                title='New Pickup Alert',
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
        
