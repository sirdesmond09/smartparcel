from django.db import models
from django.contrib.auth import get_user_model
from main.models import Parcel
from django.forms import model_to_dict
# Create your models here.
User = get_user_model()

class DesignatedParcel(models.Model):
    delivery_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='designated')
    parcel = models.ForeignKey(Parcel, on_delete=models.DO_NOTHING)
    status = models.CharField(default='pending', max_length=400)
    is_active = models.BooleanField(default=True)
    
    
    
    def __str__(self):
        return f'{self.delivery_user.id} ->> {self.parcel.id}'
    
    @property
    def user_detail(self):
        return model_to_dict(self.delivery_user, fields=['first_name', 'last_name', 'email', 'phone', 'profile_pics_url', 'address','role'])
        
    def delete(self):
        self.is_active=False
        self.save()
        return
    