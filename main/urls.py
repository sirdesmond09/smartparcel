from django.urls import  path
from . import views

urlpatterns = [
    path('locations/', views.box_locations),
    path('self_storage/', views.self_storage),
    path('customer_to_customer/', views.customer_to_customer),
    path('customer_to_courier/', views.customer_to_courier),
    path('delivery/parcels/', views.delivery_parcels),
    path('payments/', views.payments),
    path('locations/add/', views.add_location),
    path('locations/<int:location_id>/', views.location_detail),
    path('dashboard/', views.dashboard),
    path('check_codes/', views.verify_codes)
]
