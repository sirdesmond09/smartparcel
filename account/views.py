import random
import string
from rest_framework.exceptions import AuthenticationFailed, NotFound, ValidationError

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.decorators import api_view, authentication_classes, permission_classes 
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from account.permissions import IsAdmin, IsDeliveryAdminUser

from .models import LogisticPartner, User
from .serializers import ChangePasswordSerializer, ChangeRoleSerializer, FireBaseSerializer, LoginSerializer, LogisticPartnerSerializer,  UserSerializer, ConfirmResetOtpSerializer,  ResetPasswordOtpSerializer, ResetPasswordSerializer
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
            user = User.objects.create(**serializer.validated_data, role='user')
            

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
    
    """Allows a super admin to create an admin. The superadmin status is defined by a "admin" role field set in the models."""

    if request.method == 'POST':
        
        serializer = UserSerializer(data = request.data)
        
        if serializer.is_valid():

            
            password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase ) for _ in range(8))
            serializer.validated_data['password'] = password 
            user = User.objects.create(**serializer.validated_data, is_admin=True, is_active=True, role="admin")
            

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

@swagger_auto_schema(methods=['POST'], request_body=LogisticPartnerSerializer())
@api_view(['GET','POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def logistic_partner(request):
    
    """Allows a super admin to create a logistic partner. The superadmin status is defined by a "admin" role field set in the models."""
    if request.method == 'GET':
        partners = LogisticPartner.objects.filter(is_active=True)
        data = [{
            "id":partner.id,
            "name": partner.name,
            "users" : partner.users.filter(is_active=True).values()
        } for partner in partners]
        data = {
                'status'  : True,
                'message' : "Successful",
                'data' : data,
            }

        return Response(data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        
        serializer = LogisticPartnerSerializer(data = request.data)
        
        if serializer.is_valid():
            partner = LogisticPartner.objects.create(name=serializer.validated_data.pop('name'))
            
            user_data = serializer.validated_data.pop('admin')
            password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase ) for _ in range(8))
            user_data['password'] = password 
            
            User.objects.create(**user_data, is_admin=True, is_active=True, role="delivery_admin", logistic_partner=partner)
            

            serializer = LogisticPartnerSerializer(partner)
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
@permission_classes([IsDeliveryAdminUser])
def add_delivery_person(request):
    
    # request.user=User.objects.get(logistic_partner__id=1)
    if request.method == 'POST':
        
        serializer = UserSerializer(data = request.data)
        
        if serializer.is_valid():

            password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase ) for _ in range(8))
            #hash password
            serializer.validated_data['password'] = password 
            
            user = User.objects.create(**serializer.validated_data, is_active=True, role='delivery_user', logistic_partner=request.user.logistic_partner)
            

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
@permission_classes([IsAdmin])
def get_user(request):
    
    """Allows the admin to see all users  """
    if request.method == 'GET':
        user = User.objects.filter(role = 'user', is_active=True)
    
        
        serializer = UserSerializer(user, many =True)
        data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

        return Response(data, status=status.HTTP_200_OK)
    
    
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdmin])
def get_admin(request):
    
    """Allows the admin to see all users  """
    if request.method == 'GET':
        user = User.objects.filter(is_admin=True, is_active=True)
    
        
        serializer = UserSerializer(user, many =True)
        data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

        return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsDeliveryAdminUser])
def get_delivery_user(request):
    
    """Allows the admin to see all users delivery persons """
    if request.method == 'GET':
        user = User.objects.filter(is_active=True, role='delivery_user', logistic_partner=request.user.logistic_partner)
    
        
        serializer = UserSerializer(user, many =True)
        data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

        return Response(data, status=status.HTTP_200_OK)


@api_view(['GET','PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdmin])
def logistic_partner_detail(request, partner_id):
    """Allows the admin to view user profile or deactivate user's account. """
    try:
        partner = LogisticPartner.objects.get(id = partner_id, is_active=True)
    
    except LogisticPartner.DoesNotExist:
        data = {
                'status'  : False,
                'message' : "Does not exist"
            }

        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LogisticPartnerSerializer(partner)
        
        data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

        return Response(data, status=status.HTTP_200_OK)
    elif request.method=="PUT":
        serializer = LogisticPartnerSerializer(partner, data = request.data, partial=True) 

        if serializer.is_valid():
            
            serializer.save()

            data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

            return Response(data, status = status.HTTP_201_CREATED)
        
    #delete the account
    elif request.method == 'DELETE':
        partner.is_active = False
        partner.users.update(is_active=False)
        partner.save()
        

        data = {
                'status'  : True,
                'message' : "Deleted Successfully"
            }

        return Response(data, status = status.HTTP_204_NO_CONTENT)

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
                    img1 = cloudinary.uploader.upload(profile_pics, folder = 'profile_pictures/') #upload the image to cloudinary
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
@permission_classes([IsAdmin])
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
        

@swagger_auto_schema(method='post', request_body=LoginSerializer())
@api_view([ 'POST'])
def user_login(request):
    
    """Allows users to log in to the platform. Sends the jwt refresh and access tokens. Check settings for token life time."""
    
    if request.method == "POST":
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            provider = 'email'
            user = authenticate(request, email = data['email'], password = data['password'])
            if user is not None:
                if user.is_active==True:
                    if user.auth_provider == provider:
                        if 'firebase_key' in data.keys():
                            user.firebase_key = data['firebase_key']
                            user.save()
                        try:
                            
                            refresh = RefreshToken.for_user(user)

                            user_detail = {}
                            user_detail['id']   = user.id
                            user_detail['first_name'] = user.first_name
                            user_detail['last_name'] = user.last_name
                            user_detail['email'] = user.email
                            user_detail['phone'] = user.phone
                            user_detail['role'] = user.role
                            user_detail['is_admin'] = user.is_admin
                            user_detail['is_staff'] = user.is_staff
                            user_detail['profile_pics_url'] = user.profile_pics_url
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
        else:
                data = {
                    'status'  : False,
                    'error': serializer.errors
                    }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            
@swagger_auto_schema(method='post', request_body=LoginSerializer())
@api_view(['POST'])
def delivery_login(request):
    
    """Allows users to log in to the platform. Sends the jwt refresh and access tokens. Check settings for token life time."""
    
    if request.method == "POST":
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            provider = 'email'
            user = authenticate(request, email = data['email'], password = data['password'])
            if user is not None:
                if user.is_active==True and user.role == 'delivery_user':
                    if user.auth_provider == provider:
                        if 'firebase_key' in data.keys():
                            user.firebase_key = data['firebase_key']
                            user.save()
                        try:
                            
                            refresh = RefreshToken.for_user(user)

                            user_detail = {}
                            user_detail['id']   = user.id
                            user_detail['first_name'] = user.first_name
                            user_detail['last_name'] = user.last_name
                            user_detail['email'] = user.email
                            user_detail['phone'] = user.phone
                            user_detail['role'] = user.role
                            user_detail['is_admin'] = user.is_admin
                            user_detail['is_staff'] = user.is_staff
                            user_detail['profile_pics_url'] = user.profile_pics_url
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
                    'error': 'This account has not been activated or does not have permission'
                    }
                return Response(data, status=status.HTTP_403_FORBIDDEN)

            else:
                data = {
                    'status'  : False,
                    'error': 'Please provide a valid email and a password'
                    }
                return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        else:
                data = {
                    'status'  : False,
                    'error': serializer.errors
                    }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
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

    
@swagger_auto_schema(methods=['POST'], request_body=ChangeRoleSerializer())
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])   
def change_role(request, user_id):
    
    try:
        user= User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        raise NotFound(detail="User with this ID does not exist")
    
    if request.method == 'POST':
        serializer = ChangeRoleSerializer(data = request.data) 

        if serializer.is_valid():
            
            user.role=serializer.validated_data['role']
            user.save()

            data = {
                'message' : "Successful",
            }

            return Response(data, status = status.HTTP_201_CREATED)

        else:
            data = {
                'message' : "failed",
                'error' : serializer.errors,
            }

            return Response(data, status = status.HTTP_400_BAD_REQUEST)
        
        
@swagger_auto_schema(methods=['POST'], request_body=FireBaseSerializer())
@api_view(['POST'])  
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated]) 
def change_firebase_key(request):
    """Api view for updating the firebase key"""
    
    if request.method == 'POST':
        serializer = FireBaseSerializer(data = request.data)
        if serializer.is_valid():
            request.user.firebase_key = serializer.validated_data['key']
            request.user.save()
            
            return Response({'message':'success'}, status=status.HTTP_200_OK)
        else:

            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)