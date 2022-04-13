from django.db import models
from django.contrib.auth import get_user_model
from main.models import Parcel
from django.forms import model_to_dict
# Create your models here.
User = get_user_model()

class DesignatedParcel(models.Model):
    delivery_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='designated')
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE)
    status = models.CharField(default='pending', max_length=400)
    delivery_code =models.CharField(max_length=6, blank=True, null=True) 
    is_active = models.BooleanField(default=True)
    date_assigned = models.DateTimeField(auto_now_add=True)
    
    
    
    def __str__(self):
        return f'{self.delivery_user.id} ->> {self.parcel.id}'
    
    @property
    def user_detail(self):
        return model_to_dict(self.delivery_user, fields=['first_name', 'last_name', 'email', 'phone', 'profile_pics_url', 'address','role'])
    
    @property
    def sender_detail(self):
        return model_to_dict(self.parcel.user, fields=['first_name', 'last_name', 'email', 'phone', 'profile_pics_url', 'address','role'])
    
    @property
    def recipient_detail(self):
        return model_to_dict(self.parcel,
                             fields=['name',
                                     'address',
                                     'phone'])
    
    @property
    def parcel_pickup(self):
        return self.parcel.pick_up
    
    @property
    def box_address(self):
        return self.parcel.location.address
    
    def delete(self):
        self.is_active=False
        self.save()
        return
    