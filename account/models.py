from __future__ import unicode_literals

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

class User(AbstractBaseUser, PermissionsMixin):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name          = models.CharField(_('first name'),max_length = 250)
    last_name          = models.CharField(_('last name'),max_length = 250)
    email         = models.EmailField(_('email'), unique=True)
    phone         = models.CharField(_('phone'), max_length = 20)
    password      = models.CharField(_('password'), max_length=300)
    profile_pics = models.ImageField(_('profile picture'), null=True, blank=True)
    profile_pics_url = models.CharField(_('profile picture url'), max_length = 5000, null=True, blank=True)
    is_active     = models.BooleanField(_('active'), default=False)
    is_staff     = models.BooleanField(_('staff'), default=False)
    is_admin    = models.BooleanField(_('admin'), default=False)
    is_superuser    = models.BooleanField(_('superuser'), default=False)
    date_joined   = models.DateTimeField(_('date joined'), auto_now_add=True)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email'))
    
    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email
    
    
    @property
    def self_storages(self):
        return self.self_storage.filter(is_active=True).values(
            'id',
            'duration',
            'location__address',
            'status',
            'drop_off',
            'pick_up',
            'created_at')
    
    @property
    def customer_to_customer(self):
        return self.peer_to_peer.filter(is_active=True).values(
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
    def payment_history(self):
        return self.payments.filter(is_active=True).values()
    
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