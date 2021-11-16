from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class BoxLocation(models.Model):
    location=models.CharField(max_length=200)
    address = models.CharField(max_length=3000)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def delete(self):
        self.is_active=False
        self.save()
        return 
    
class SelfStorage(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='self_storage')
    duration = models.CharField(max_length=200)
    location = models.ForeignKey(BoxLocation, on_delete=models.DO_NOTHING, related_name='self_storage')
    status = models.CharField(default='pending', max_length=300)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    
    def delete(self):
        self.is_active=False
        self.save()
        return 
    
    
class CustomerToCustomer(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='peer_to_peer')
    name = models.CharField(max_length=500)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    location = models.ForeignKey(BoxLocation, on_delete=models.DO_NOTHING, related_name='peer_to_peer')
    status = models.CharField(default='pending', max_length=300)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    
    def delete(self):
        self.is_active=False
        self.save()
        return 