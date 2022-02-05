from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([Payments, 
                     Parcel, 
                     BoxLocation, 
                     BoxSize,
                     CardDetail,
                     Compartment,
                     Category
                     ])