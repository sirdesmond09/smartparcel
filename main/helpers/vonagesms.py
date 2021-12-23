from rest_framework.exceptions import ValidationError
import  vonage
import os

key = os.getenv("VONAGE_KEY")
secret = os.getenv('VONAGE_SECRET')
client = vonage.Client(key=key, secret=secret)
sms = vonage.Sms(client)


def send_sms(reason, code, phone, address):
    
    if reason=='delivery_code':
        message = f"Hello, your parcel is on the way. Kindly use the code {code} to verify.\nThanks\nSmart Parcel."
        
    if reason=='drop_off':
        message = f"Hello, your parcel has been dropped off. Kindly use the code {code} to pick it up at {address}.\nThanks\nSmart Parcel."
    
    responseData = sms.send_message(
        {
            "from": 'SmartParcel',
            "to": phone,
            "text": message
        }
    )

    if responseData["messages"][0]["status"] == "0":
        return
    else:
        raise ValidationError(detail = f"Message failed with error: {responseData['messages'][0]['error-text']}")