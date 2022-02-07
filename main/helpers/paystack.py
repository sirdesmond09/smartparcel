import requests
import os
from main.models import CardDetail

from rest_framework import serializers
secret = os.getenv('secret_key')

def verify_payment(reference, allow_save, user):
    url = f'https://api.paystack.co/transaction/verify/{reference}'
    response = requests.get(url=url, headers={
        "content-type":"application/json",
        "Authorization" : f"Bearer {secret}"
        }
    )
    
    try:
        data = response.json()['data']
        # print(data)
        # print()
        if response.status_code == 200 and data['status'] == 'success':
            print(allow_save)
            if allow_save == True:
                data_ = data['authorization']
                # print(data_)
                card_detail ={
                    'authorization_code': data_['authorization_code'], 
                    'bin': data_['bin'], 
                    'last4':data_['last4'], 
                    'exp_month': data_['exp_month'], 
                    'exp_year': data_['exp_year'], 
                    'card_type': data_['card_type'], 
                    'bank': data_['bank'], 
                    'country_code': data_['country_code'],
                    'account_name': data_['account_name']}
                
                CardDetail.objects.create(**card_detail, user=user)
            return {
                "amount": data['amount'],
                "currency": data['currency'],
                "transaction_date": data["transaction_date"],
                'reference':data['reference']
                }
        
        return False
    except Exception as e:
        raise serializers.ValidationError(detail='Unable to verify transaction')
    
    
    