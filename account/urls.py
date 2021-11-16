from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'account'

urlpatterns = [

    #users
    path('user/add_user/', views.add_user),
    path('user/add_admin/', views.add_admin),
    path('user/all_users/', views.get_user),
    path('user/profile/', views.user_detail),
    path('user/reset_password/', views.reset_password),

    path('user/<uuid:user_id>/', views.get_user_detail),
    

    #user login
    path('auth/', views.user_login),
    path('auth/token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    
    #social auth 
    path('auth/social/', include('social_auth.urls'), name="social-login" ),
    
    path('user/forget_password/', include('django_rest_passwordreset.urls', namespace='forget_password')),
    
    path('otp/', views.otp_verification),
    path('otp/new/', views.reset_otp),

]

