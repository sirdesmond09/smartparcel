from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'account'

urlpatterns = [

    #users
    path('user/add_user/', views.add_user),
    path('user/add_admin/', views.add_admin),
    path('logistic_partners/', views.logistic_partner),
    path('logistic_partners/<int:partner_id>', views.logistic_partner_detail),
    path('user/add_delivery_person/', views.add_delivery_person),
    path('user/all_users/', views.get_user),
    path('user/all_admin/', views.get_admin),
    path('user/delivery_persons/', views.get_delivery_user),
    path('user/profile/', views.user_detail),
    path('user/reset_password/', views.reset_password),
    path('user/<uuid:user_id>/', views.get_user_detail),
    path('user/admin/change_role/<uuid:user_id>', views.change_role),
    

    #user login
    path('auth/', views.user_login),
    path('auth/delivery/', views.delivery_login),
    path('auth/token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    
    #social auth 
    path('auth/social/', include('social_auth.urls'), name="social-login" ),
    
    # path('user/forget_password/', include('django_rest_passwordreset.urls', namespace='forget_password')),
    path('user/forget_password/', views.forgot_password),
    path('user/forgot_password/confirm_otp/', views.confirm_password_reset),
    path('user/forgot_password/confirm_password/', views.forget_password_complete),
    
    
    path('otp/', views.otp_verification),
    path('otp/new/', views.reset_otp),
    
    path('user/firebase_key/update/', views.change_firebase_key)

]

