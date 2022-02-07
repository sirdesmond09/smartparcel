from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff', 'is_admin', 'is_active')
    list_editable = ['is_staff', 'is_admin', 'is_active']
    
admin.site.register(User, CustomUserAdmin)
