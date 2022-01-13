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
    path('locations/update_city/<str:location>/', views.update_location),
    path('dashboard/', views.dashboard),
    path('parcel/drop/', views.drop_codes),
    path('parcel/collect/', views.pick_codes),
    path("download_api_keys/", views.get_center_keys),
    path("get_api_keys/", views.get_keys)
]
