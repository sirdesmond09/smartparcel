from django.urls import  path
from . import views

urlpatterns = [
    path('delivery/designate/', views.assign_parcel),
    path('delivery/designate/<int:id>', views.assign_parcel_detail),
    path('delivery/personal/', views.get_designated_parcels),
    path('delivery/mark_complete/', views.mark_complete)
]
