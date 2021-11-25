import requests
import os

from rest_framework import serializers
secret = os.getenv('secret_key')

def verify_payment(reference):
    url = f'https://api.paystack.co/transaction/verify/{reference}'
    response = requests.get(url=url, headers={
        "content-type":"application/json",
        "Authorization" : f"Bearer {secret}"
        }
    )
    # print(response)
    
    try:
        # print(response.json())
        data = response.json()['data']
        # print(data)
        # print()
        if response.status_code == 200 and data['status'] == 'success':
            return {
                "amount": data['amount'],
                "currency": data['currency'],
                "transaction_date": data["transaction_date"],
                'reference':data['reference']
                }
        
        return False
    except Exception:
        raise serializers.ValidationError(detail='Unable to verify transaction')
    
    
    