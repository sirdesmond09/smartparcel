from email.policy import default
from typing import DefaultDict
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.core.signing import Signer
from account.models import LogisticPartner
from config import settings
import uuid

User = get_user_model()

signer = Signer(key=settings.Common.SECRET_KEY)


def create_box_key():
    key = str(uuid.uuid4()).replace("-", "")
    return signer.sign(key)


def get_partner():
    return LogisticPartner.objects.filter(is_active=True).first()

# Create your models here.
class BoxLocation(models.Model):
    center_apikey = models.CharField(default = create_box_key, unique=True, blank=True,null=True,max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    location=models.CharField(max_length=200)
    center_name = models.CharField(max_length=300)
    address = models.CharField(max_length=3000)
    no_of_compartment = models.IntegerField()
    available_space = models.IntegerField()
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def delete(self):
        self.is_active=False
        self.save()
        return 
    
class Parcel(models.Model):
    STATUS_CHOICE = (('pending','Pending'),
                     ('assigned', 'Assigned'),
                     ('dropped', 'Dropped'),
                     ('completed', 'Completed'))
    
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,20}$', message="Phone number must be entered in the format: '+2341234567890'. Up to 20 digits allowed.")
    
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parcels', null=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True, validators=[phone_regex])
    email = models.EmailField(null=True, blank=True)
    duration = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    location = models.ForeignKey(BoxLocation, on_delete=models.CASCADE, null=True, related_name='parcels')
    description = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    pick_up = models.CharField(max_length=6, blank=True, null=True)
    drop_off = models.CharField(max_length=6, blank=True, null=True)
    dropoff_used = models.BooleanField(default=False)
    pickup_used = models.BooleanField(default=False)
    parcel_type = models.CharField(null=True, blank=True, max_length=400)
    status = models.CharField(default='pending', max_length=300, choices=STATUS_CHOICE)
    compartment = models.IntegerField(null=True, blank=True)
    delivery_partner = models.ForeignKey(LogisticPartner, on_delete=models.CASCADE, null=True, blank=True, default=get_partner)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    
    def delete(self):
        self.is_active=False
        self.save()
        return 
    
    
    def __str__(self):
        return f'{self.id}>>{self.parcel_type}>>{self.status}' 
    
        
    

    
class Payments(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE,null=True,related_name='payments')
    amount = models.FloatField()
    payment_for = models.CharField(max_length=300)
    reference = models.CharField(max_length=300)
    currency= models.CharField(max_length=300)
    transaction_date = models.DateTimeField()
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    
    def delete(self):
        self.is_active=False
        self.save()
        return 
    
    def __str__(self):
        return self.reference
    
    
    

class CardDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    authorization_code=models.CharField(max_length=255)
    bin = models.CharField(max_length=250)
    last4 = models.CharField(max_length=255)
    exp_month = models.CharField(max_length=255)
    exp_year = models.CharField(max_length=255)
    bank = models.CharField(max_length=244, null=True)
    card_type = models.CharField(max_length=255)
    country_code = models.CharField(max_length=255)
    account_name = models.CharField(max_length=600, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def delete(self):
        self.is_active=False
        self.save()
        return 
    
    def __str__(self):
        return f"{self.card_type} card for user with ID {self.user.id}"
    