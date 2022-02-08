from django.urls import  path
from . import views

urlpatterns = [
    path('categories/', views.add_category),
    path('categories/<int:category_id>/compartment/<int:compartent_id>', views.set_size),
    path('sizes/', views.add_sizes),
    path('sizes/<size_id>', views.size_detail),
    path('locations/', views.box_locations),
    path('self_storage/', views.self_storage),
    path('customer_to_customer/', views.customer_to_customer),
    path('customer_to_courier/', views.customer_to_courier),
    path('delivery/parcels/', views.delivery_parcels),
    path('payments/', views.payments),
    path('locations/add/', views.add_location),
    path('locations/<int:location_id>/', views.location_detail),
    path('all_parcels/', views.all_parcels),
    path('locations/update_city/<str:location>/', views.update_location),
    path('dashboard/', views.dashboard),
    path('parcel/drop/', views.drop_codes),
    path('parcel/collect/', views.pick_codes),
    path("download_api_keys/", views.get_center_keys),
    path("get_api_keys/", views.get_keys),
    path("card/remove/<int:card_id>", views.delete_card)
]
