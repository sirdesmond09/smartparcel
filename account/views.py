from rest_framework.exceptions import AuthenticationFailed

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.decorators import api_view, authentication_classes, permission_classes 
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import User
from .serializers import ChangePasswordSerializer,  UserSerializer, ConfirmResetOtpSerializer,  ResetPasswordOtpSerializer, ResetPasswordSerializer
from .signals import NewOtpSerializer, OTPVerifySerializer


from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.signals import user_logged_in

import cloudinary
import cloudinary.uploader


@swagger_auto_schema(methods=['POST'], request_body=UserSerializer())
@api_view(['POST'])
def add_user(request):
    
    """ Allows the user to be able to sign up on the platform """

    if request.method == 'POST':
        
        serializer = UserSerializer(data = request.data)
        
        if serializer.is_valid():
            
            #hash password
            serializer.validated_data['password'] = make_password(serializer.validated_data['password']) #hash the given password
            user = User.objects.create(**serializer.validated_data)
            

            serializer = UserSerializer(user)
            data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

            return Response(data, status = status.HTTP_201_CREATED)

        else:
            data = {
                'status'  : False,
                'message' : "Unsuccessful",
                'error' : serializer.errors,
            }

            return Response(data, status = status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(methods=['POST'], request_body=UserSerializer())
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def add_admin(request):
    
    """Allows a super admin to create an admin. The superadmin status is defined by an "is_staff" field set in the models."""

    if request.method == 'POST':
        
        serializer = UserSerializer(data = request.data)
        
        if serializer.is_valid():

            
            #hash password
            serializer.validated_data['password'] = make_password(serializer.validated_data['password']) #hash the given password
            user = User.objects.create(**serializer.validated_data, is_admin=True, is_staff=True)
            

            serializer = UserSerializer(user)
            data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

            return Response(data, status = status.HTTP_201_CREATED)

        else:
            data = {
                'status'  : False,
                'message' : "Unsuccessful",
                'error' : serializer.errors,
            }

            return Response(data, status = status.HTTP_400_BAD_REQUEST)



 

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_user(request):
    
    """Allows the admin to see all users (both admin and normal users) """
    if request.method == 'GET':
        user = User.objects.filter(is_active=True)
    
        
        serializer = UserSerializer(user, many =True)
        data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

        return Response(data, status=status.HTTP_200_OK)


#Get the detail of a single user by their ID

@swagger_auto_schema(methods=['PUT', 'DELETE'], request_body=UserSerializer())
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_detail(request):
    """Allows the logged in user to view their profile, edit or deactivate account. Do not use this view for changing password or resetting password"""
    
    try:
        user = User.objects.get(id = request.user.id, is_active=True)
    
    except User.DoesNotExist:
        data = {
                'status'  : False,
                'message' : "Does not exist"
            }

        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        
        data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

        return Response(data, status=status.HTTP_200_OK)

    #Update the profile of the user
    elif request.method == 'PUT':
        serializer = UserSerializer(user, data = request.data, partial=True) 

        if serializer.is_valid():
            
            
            #upload profile picture
            if 'profile_pics' in serializer.validated_data.keys():
                try:
                    profile_pics = serializer.validated_data['profile_pics'] #get the image file from the request 
                    img1 = cloudinary.uploader.upload(profile_pics, folder = 'edm/profile_pictures/') #upload the image to cloudinary
                    serializer.validated_data['profile_pics'] = "" #delete the image file
                    serializer.validated_data['profile_pics_url'] = img1['secure_url'] #save the image url 
                except Exception:
                    data = {
                        'status'  : False,
                        'error' : "Unable to upload profile picture"
                    }

                    return Response(data, status = status.HTTP_400_BAD_REQUEST)
            
            serializer.save()

            data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

            return Response(data, status = status.HTTP_201_CREATED)

        else:
            data = {
                'status'  : False,
                'message' : "Unsuccessful",
                'error' : serializer.errors,
            }

            return Response(data, status = status.HTTP_400_BAD_REQUEST)

    #delete the account
    elif request.method == 'DELETE':
        user.is_active = False
        user.save()

        data = {
                'status'  : True,
                'message' : "success"
            }

        return Response(data, status = status.HTTP_204_NO_CONTENT)
    

@api_view(['GET', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_user_detail(request, user_id):
    """Allows the admin to view user profile or deactivate user's account. """
    try:
        user = User.objects.get(id = user_id, is_active=True)
    
    except User.DoesNotExist:
        data = {
                'status'  : False,
                'message' : "Does not exist"
            }

        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        
        data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

        return Response(data, status=status.HTTP_200_OK)

    #delete the account
    elif request.method == 'DELETE':
        user.is_active = False
        user.save()

        data = {
                'status'  : True,
                'message' : "Deleted Successfully"
            }

        return Response(data, status = status.HTTP_204_NO_CONTENT)



@swagger_auto_schema(methods=['POST'],  request_body=NewOtpSerializer())
@api_view(['POST'])
def reset_otp(request):
    if request.method == 'POST':
        serializer = NewOtpSerializer(data = request.data)
        if serializer.is_valid():
            data = serializer.get_new_otp()
            
            return Response(data, status=status.HTTP_200_OK)
        
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
        
            
@swagger_auto_schema(methods=['POST'], request_body=OTPVerifySerializer())
@api_view(['POST'])
def otp_verification(request):
    
    """Api view for verifying OTPs """

    if request.method == 'POST':

        serializer = OTPVerifySerializer(data = request.data)

        if serializer.is_valid():
            data = serializer.verify_otp()
            
            return Response(data, status=status.HTTP_200_OK)
        else:

            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        

@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT, 
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='user@email.com'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
    }
))
@api_view([ 'POST'])
def user_login(request):
    
    """Allows users to log in to the platform. Sends the jwt refresh and access tokens. Check settings for token life time."""
    
    if request.method == "POST":
        provider = 'email'
        user = authenticate(request, email = request.data['email'], password = request.data['password'])
        if user is not None:
            if user.is_active==True:
                if user.auth_provider == provider:
                    try:
                        
                        refresh = RefreshToken.for_user(user)

                        user_detail = {}
                        user_detail['id']   = user.id
                        user_detail['first_name'] = user.first_name
                        user_detail['last_name'] = user.last_name
                        user_detail['username'] = user.username
                        user_detail['email'] = user.email
                        user_detail['phone'] = user.phone
                        user_detail['is_admin'] = user.is_admin
                        user_detail['access'] = str(refresh.access_token)
                        user_detail['refresh'] = str(refresh)
                        user_logged_in.send(sender=user.__class__,
                                            request=request, user=user)

                        data = {
                        'status'  : True,
                        'message' : "Successful",
                        'data' : user_detail,
                        }
                        return Response(data, status=status.HTTP_200_OK)
                    

                    except Exception as e:
                        raise e
                else:
                    raise AuthenticationFailed(
                    detail='Please continue your login using ' + user.auth_provider)
            else:
                data = {
                'status'  : False,
                'error': 'This account has not been activated'
                }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        else:
            data = {
                'status'  : False,
                'error': 'Please provide a valid email and a password'
                }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        
        
@swagger_auto_schema(methods=['POST'], request_body=ChangePasswordSerializer())
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])   
def reset_password(request):
    """Allows users to edit password when logged in."""
    user = request.user
    if request.method == 'POST':
        serializer = ChangePasswordSerializer(data = request.data)
        if serializer.is_valid():
            if check_password(serializer.validated_data['old_password'], user.password):
                if serializer.check_pass():
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    
                    data = {
                        'status'  : True,
                        'message': "Successfully saved password"
                        }
                    return Response(data, status=status.HTTP_202_ACCEPTED) 
                else:
                    
                    data = {
                        'status'  : False,
                        'error': "Please enter matching passwords"
                        }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)   
        
            else:
                
                data = {
                    'status'  : False,
                    'error': "Incorrect password"
                    }
                return Response(data, status=status.HTTP_403_FORBIDDEN)   
        
            
        else:
            
            data = {
                'status'  : False,
                'error': serializer.errors
                }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)   
        


@swagger_auto_schema(methods=['POST'], request_body=ResetPasswordOtpSerializer())
@api_view(['POST'])
def forgot_password(request):
    
    """Api view for forget password OTPs """

    if request.method == 'POST':

        serializer = ResetPasswordOtpSerializer(data = request.data)

        if serializer.is_valid():
            data = serializer.get_otp()
                        
            return Response(data, status=status.HTTP_200_OK)
        else:

            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        

@swagger_auto_schema(methods=['POST'], request_body=ConfirmResetOtpSerializer())
@api_view(['POST'])
def confirm_password_reset(request):
    """Api view for verifying reset password OTPs """

    if request.method == 'POST':

        serializer = ConfirmResetOtpSerializer(data = request.data)

        if serializer.is_valid():
            data = serializer.verify_otp()
            
            return Response(data, status=status.HTTP_200_OK)
        else:

            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
    
@swagger_auto_schema(methods=['POST'], request_body=ResetPasswordSerializer())
@api_view(['POST'])  
def forget_password_complete(request):
    """Api view for completing reset password OTPs """
    
    if request.method == 'POST':
        serializer = ResetPasswordSerializer(data = request.data)
        if serializer.is_valid():
            data = serializer.reset_password()
            
            return Response(data, status=status.HTTP_200_OK)
        else:

            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    
    
    
# class CookieTokenRefreshView(TokenRefreshView):
#     def finalize_response(self, request, response, *args, **kwargs):
#         if response.data.get('refresh'):
#             cookie_max_age = 120 * 60 * 60 # 5 days
#             response.set_cookie('refresh', response.data['refresh'], max_age=cookie_max_age, httponly=True)
#             del response.data['refresh']
#         return super().finalize_response(request, response, *args, **kwargs)
#     serializer_class = CookieTokenRefreshSerializer
    
    

# @api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
# def logout_view(request):
#         try:
#             refresh_token = request.COOKIES.get('refresh')
#             token = RefreshToken(refresh_token)
#             token.blacklist()

#             res = Response(status=status.HTTP_205_RESET_CONTENT)
#             res.delete_cookie('refresh')
#             return res
#         except Exception as e:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


    