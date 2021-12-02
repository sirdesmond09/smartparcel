from django.urls import  path
from . import views
urlpatterns = [
    path('locations/', views.box_locations),
    path('self_storage/', views.self_storage),
    path('customer_to_customer/', views.customer_to_customer),
    path('payments/', views.payments),
    path('locations/add/', views.add_location),
    path('dashboard/', views.dashboard)
]
