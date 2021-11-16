from django.urls import  path
from . import views
urlpatterns = [
    path('parcel_centers/', views.box_locations),
    path('self_storage/', views.self_storage),
    path('customer_to_customer/', views.customer_to_customer)
]
