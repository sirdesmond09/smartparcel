from django.contrib import admin
from .models import Parcel, Payments

# Register your models here.
admin.site.register([Parcel, Payments])