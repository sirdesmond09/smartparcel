from typing import DefaultDict
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

# Create your models here.
class BoxLocation(models.Model):
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
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,20}$', message="Phone number must be entered in the format: '+2341234567890'. Up to 20 digits allowed.")
    
    
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='parcels')
    name = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True, validators=[phone_regex])
    email = models.EmailField(null=True, blank=True)
    duration = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    location = models.ForeignKey(BoxLocation, on_delete=models.DO_NOTHING, related_name='parcels')
    city = models.CharField(max_length=200, null=True, blank=True)
    pick_up = models.CharField(max_length=6, blank=True, null=True)
    drop_off = models.CharField(max_length=6, blank=True, null=True)
    dropoff_used = models.BooleanField(default=False)
    pickup_used = models.BooleanField(default=False)
    parcel_type = models.CharField(null=True, blank=True, max_length=400)
    status = models.CharField(default='pending', max_length=300)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    
    def delete(self):
        self.is_active=False
        self.save()
        return 
    
    
        
    

    
class Payments(models.Model):
    user=models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='payments')
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