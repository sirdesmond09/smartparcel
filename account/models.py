from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from .managers import UserManager
import uuid
# models

AUTH_PROVIDERS = {'facebook': 'facebook', 
                  'google': 'google',  
                  'email': 'email'}

class LogisticPartner(models.Model):
    name = models.CharField(max_length=255, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def delete(self):
        self.is_active=False
        self.save()
        return 
    
    
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICE = (('user','User'),
                    ('delivery_admin', 'Delivery Admin'),
                    ('admin', 'Admin'),
                    ('delivery_user', 'Delivery User'))
    
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,20}$', message="Phone number must be entered in the format: '+2341234567890'. Up to 20 digits allowed.")
    
    
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name          = models.CharField(_('first name'),max_length = 250)
    last_name          = models.CharField(_('last name'),max_length = 250)
    email         = models.EmailField(_('email'), unique=True)
    phone         = models.CharField(_('phone'), max_length = 20, unique=True, validators=[phone_regex])
    password      = models.CharField(_('password'), max_length=300)
    profile_pics = models.ImageField(_('profile picture'), null=True, blank=True)
    profile_pics_url = models.CharField(_('profile picture url'), max_length = 5000, null=True, blank=True)
    address = models.CharField(_('address'), max_length = 5000, null=True, blank=True)
    # admin = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True, blank=True)
    is_active     = models.BooleanField(_('active'), default=False)
    is_staff     = models.BooleanField(_('staff'), default=False)
    is_admin    = models.BooleanField(_('admin'), default=False)
    role = models.CharField(default='user', max_length=300, choices=ROLE_CHOICE)
    logistic_partner = models.ForeignKey(LogisticPartner, null=True, blank=True, on_delete=models.CASCADE, related_name="users")
    is_superuser    = models.BooleanField(_('superuser'), default=False)
    date_joined   = models.DateTimeField(_('date joined'), auto_now_add=True)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email'))
    firebase_key =  models.TextField(null=True, blank=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email
    
    @property
    def saved_cards(self):
        return self.cards.order_by('-date_added').values()[:2]
    
    @property
    def self_storages(self):
        return self.parcels.filter(is_active=True, parcel_type='self_storage').values(
            'id',
            'duration',
            'location__address',
            'status',
            'drop_off',
            'pick_up',
            'created_at')
    
    @property
    def customer_to_customer(self):
        return self.parcels.filter(is_active=True, parcel_type='customer_to_customer').values(
            'id',
            'name',
            'email',
            'phone',
            'location__address',
            'status',
            'drop_off',
            'pick_up',
            'created_at')
    
    @property
    def customer_to_courier(self):
        return self.parcels.filter(is_active=True, parcel_type='customer_to_courier').values(
            'id',
            'name',
            'email',
            'phone',
            'location__address',
            'city',
            'status',
            'drop_off',
            'pick_up',
            'created_at')
  
    @property
    def payment_history(self):
        return self.payments.filter(is_active=True).values()
    
    @property
    def parcel_stats(self):
        data = {
            'pending': self.parcels.filter(status='pending').count(),
            'dropped': self.parcels.filter(status='dropped').count(),
            'assigned': self.parcels.filter(status='assigned').count(),
            'completed': self.parcels.filter(status='completed').count(), 
        }
        
        return data
class OTP(models.Model):
    code = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    

    
    def __str__(self):
        return self.code
    
    
class ResetPasswordOTP(models.Model):
    code = models.CharField(max_length=6)
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_password_otps')
    
    def __str__(self):
        return self.code + " for " + self.email