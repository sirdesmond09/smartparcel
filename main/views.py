from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import BoxLocation, CustomerToCustomer, Payments, SelfStorage
from .serializers import BoxLocationSerializer, CustomerToCusomterSerializer, SelfStorageSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .helpers.paystack import verify_payment
import random
import string

from main.helpers import paystack

def generate_code(n):
    codes = []
    for i in range(2):
        code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))
        codes.append(code)
    return codes
    
@api_view(['GET'])
def box_locations(request):
    if request.method == "GET":
        locations = BoxLocation.objects.values_list('location', flat=True).distinct()
        # print(locations)
        data =[
            {'name': location,
             'centers': BoxLocation.objects.filter(location=location).values()
             } for location in locations
            
            ]
        

        return Response(data, status=status.HTTP_200_OK)
    
# @swagger_auto_schema(methods=["POST"], request_body=BoxLocationSerializer())
# @api_view(['POST'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
# def add_location(request):
    

@swagger_auto_schema(methods=["POST"], request_body=SelfStorageSerializer())
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def self_storage(request):
    if request.method == 'POST':
        serializer = SelfStorageSerializer(data=request.data)
        if serializer.is_valid():
            if 'user' in serializer.validated_data.keys():
                serializer.validated_data.pop('user')
                
                
            reference = serializer.validated_data.pop('reference')
            payment_data = verify_payment(reference=reference) 
            if payment_data != False:
                
                pick_up, drop_off = generate_code(6)
                
                Payments.objects.create(**payment_data, user=request.user, payment_for='self_storage') 
                # print(serializer.validated_data)
                
                storage = SelfStorage.objects.create(**serializer.validated_data, user=request.user, drop_off=drop_off, pick_up=pick_up)
                
                serializer = SelfStorageSerializer(storage)
                
                data = {"message":"success",
                        "data":serializer.data}
                return Response(data, status=status.HTTP_200_OK)
            else:
                errors = {
                    "message":"failed",
                    "errors":"Unable to verify payment"}
            return Response(errors, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        else:
            errors = {"message":"failed",
                    "errors":serializer.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        
@swagger_auto_schema(methods=["POST"], request_body=CustomerToCusomterSerializer())
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def customer_to_customer(request):
    if request.method == 'POST':
        serializer = CustomerToCusomterSerializer(data=request.data)
        if serializer.is_valid():
            if 'user' in serializer.validated_data.keys():
                serializer.validated_data.pop('user')
                
                
            reference = serializer.validated_data.pop('reference')
            
            payment_data = verify_payment(reference=reference) 
            
            if payment_data != False:
                
                pick_up, drop_off = generate_code(6)
                
                Payments.objects.create(**payment_data, user=request.user, payment_for='customer_to_customer') 
                # print(serializer.validated_data)
                
                c2c = CustomerToCustomer.objects.create(**serializer.validated_data, user=request.user, drop_off=drop_off, pick_up=pick_up)
                
                serializer = CustomerToCusomterSerializer(c2c)
                
                data = {"message":"success",
                        "data":serializer.data}
                return Response(data, status=status.HTTP_200_OK)
            else:
                errors = {
                    "message":"failed",
                    "errors":"Unable to verify payment"}
            return Response(errors, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        else:
            errors = {"message":"failed",
                    "errors":serializer.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)