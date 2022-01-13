from firebase_admin import messaging

def send_notification(notice_for, user):
    
    firebase_key = user.firebase_key
    
    
    if notice_for == "dropped":
        title = 'Drop off code used'
        body = "Your parcel has been dropped and ready for pickup"
    elif notice_for == "picked":
        title = 'Pickup code used'
        body = "Your parcel has been picked."
    else:
        title = ""
        body=""
    
    message = messaging.Message(
        token=firebase_key,
        notification=messaging.Notification(
            title=title,
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
        

    
