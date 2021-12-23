from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from account.permissions import IsDeliveryAdminUser
from .models import BoxLocation, Parcel, Payments
from .serializers import AddLocationSerializer, BoxLocationSerializer, CustomerToCourierSerializer, CustomerToCusomterSerializer, ParcelSerializer, PaymentsSerializer, SelfStorageSerializer, UpdateLocationSerializer, VerifySerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .helpers.paystack import verify_payment
import random
import string
from django.utils import timezone

def generate_code(n):
    codes = []
    for i in range(2):
        code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))
        codes.append(code)
    return codes
    
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def box_locations(request):
    if request.method == "GET":
        locations = BoxLocation.objects.values_list('location', flat=True).distinct()
        data =[
            {'name': location,
             'centers': BoxLocation.objects.filter(location=location).values()
             } for location in locations
            
            ]
        

        return Response(data, status=status.HTTP_200_OK)
    
@swagger_auto_schema(methods=["POST"], request_body=AddLocationSerializer())
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def add_location(request):
    if request.method=='POST':
        serializer = AddLocationSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.add_location(request)
            
            data = {"message":"success"}
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            errors = {
                "message":"failed",
                "errors":serializer.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        

@swagger_auto_schema(methods=['PUT', 'DELETE'], request_body=BoxLocationSerializer())
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def location_detail(request, location_id):
    """Allows the logged in user to view their profile, edit or deactivate account. Do not use this view for changing password or resetting password"""
    
    try:
        obj = BoxLocation.objects.get(id = location_id, is_active=True)
    
    except BoxLocation.DoesNotExist:
        data = {
                'status'  : False,
                'message' : "Does not exist"
            }

        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BoxLocationSerializer(obj)
        
        data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = BoxLocationSerializer(obj, data = request.data, partial=True) 

        if serializer.is_valid():
            
            serializer.save()

            data = {
                'message' : "Successful",
                'data' : serializer.data,
            }

            return Response(data, status = status.HTTP_201_CREATED)

        else:
            data = {

                'message' : "Unsuccessful",
                'error' : serializer.errors,
            }

            return Response(data, status = status.HTTP_400_BAD_REQUEST)

    #delete the account
    elif request.method == 'DELETE':
        obj.is_active = False
        obj.save()

        data = {
                'message' : "success"
            }

        return Response(data, status = status.HTTP_204_NO_CONTENT)
    


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
                
                try:
                    location = BoxLocation.objects.get(id=serializer.validated_data.pop('location'), is_active=True)
                except BoxLocation.DoesNotExist:
                    raise ValidationError(detail='Location unavailable')
                if int(location.available_space) == 0:
                    raise ValidationError(detail='Available spaces used up for this location')
                
                
                pick_up, drop_off = generate_code(4)
                
                Payments.objects.create(**payment_data, user=request.user, payment_for='self_storage') 
                # print(serializer.validated_data)
                
                storage = Parcel.objects.create(**serializer.validated_data, user=request.user,location=location, drop_off=drop_off, pick_up=pick_up, parcel_type='self_storage')
                
                location.available_space-=1
                location.save()
                
                serializer = ParcelSerializer(storage)
                
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
                
                # print(serializer.validated_data)
                
                try:
                    location = BoxLocation.objects.get(id=serializer.validated_data.pop('location'), is_active=True)
                except BoxLocation.DoesNotExist:
                    raise ValidationError(detail='Location unavailable')
                
                if int(location.available_space) == 0:
                    raise ValidationError(detail='Available spaces used up for this location') 
                
                pick_up, drop_off = generate_code(4)
                
                Payments.objects.create(**payment_data, user=request.user, payment_for='customer_to_customer') 
                
                
                storage = Parcel.objects.create(**serializer.validated_data, user=request.user,location=location, drop_off=drop_off, pick_up=pick_up, parcel_type='customer_to_customer')
                
                location.available_space-=1
                location.save()
                
                serializer = ParcelSerializer(storage)
                
                
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
        

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def payments(request):
    if request.method == 'GET':
        obj = Payments.objects.filter(is_active=True)
        serializer = PaymentsSerializer(obj, many=True)
        data = {"message":"success",
                        "data":serializer.data}
        
        return Response(data, status=status.HTTP_200_OK)
        

@api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAdminUser])
def dashboard(request):
    c2c = Payments.objects.filter(payment_for='customer_to_customer').values_list('amount',flat=True)
    self_storage = Payments.objects.filter(payment_for='self_storage').values_list('amount',flat=True)
    courier = Payments.objects.filter(payment_for='courier').values_list('amount',flat=True)
    
    
    dates = [(timezone.now() - timezone.timedelta(days=x)).date() for x in range(1,8) ]
    # print(dates)
    daily_stats = {
            str(date): {
                "num_of_transactions":Payments.objects.filter(transaction_date__date=date, is_active=True).count(),
                "sum_total" : sum(Payments.objects.filter(transaction_date__date=date, is_active=True).values_list('amount', flat=True))
            }
            
            for date in dates
        }
    transaction_stats = {
        'customer_to_customer':{
            'num_of_transactions':len(c2c),
            'sum_total':sum(c2c)
        },
        'self_storage':{
            'num_of_transactions':len(self_storage),
            'sum_total':sum(self_storage)
        },
        'courier':{
            'num_of_transactions':len(courier),
            'sum_total':sum(courier)
        }
    }
    
    data = {
        "message":"success",
        "data":{
            'transaction_stats':transaction_stats,
            'daily_stats':daily_stats
                    }
            }
    
    return Response(data, status=status.HTTP_200_OK)

        
@swagger_auto_schema(methods=["POST"], request_body=VerifySerializer())
@api_view(['GET', 'POST'])
def verify_codes(request):
    if request.method == "GET":
        codes = Parcel.objects.filter(is_active=True).values('id', 'drop_off', 'pick_up')
        data = {"message":"success",
                "data":codes
            }
        return Response(data, status=status.HTTP_200_OK)
    
    
    if request.method == 'POST':
        serializer = VerifySerializer(data = request.data)
        if serializer.is_valid():
            changed = serializer.change_status()
            if changed == True:
                data = {"message":"success"
                        }
                return Response(data, status=status.HTTP_204_NO_CONTENT)
            
            else:
                data = {"message":"failed"
                        }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(methods=["POST"], request_body=CustomerToCourierSerializer())
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def customer_to_courier(request):
    if request.method == 'POST':
        serializer = CustomerToCourierSerializer(data=request.data)
        if serializer.is_valid():
            if 'user' in serializer.validated_data.keys():
                serializer.validated_data.pop('user')
                
                
            reference = serializer.validated_data.pop('reference')
            
            payment_data = verify_payment(reference=reference) 
            
            if payment_data != False:
                
                
                try:
                    location = BoxLocation.objects.get(id=serializer.validated_data.pop('location'), is_active=True)
                except BoxLocation.DoesNotExist:
                    raise ValidationError(detail='Location unavailable')
                
                if int(location.available_space) == 0:
                    raise ValidationError(detail='Available spaces used up for this location') 
                
                
                pick_up, drop_off = generate_code(4)
                
                Payments.objects.create(**payment_data, user=request.user, payment_for='customer_to_courier') 
                # print(serializer.validated_data)
                
                storage = Parcel.objects.create(**serializer.validated_data, user=request.user,location=location, drop_off=drop_off, pick_up=pick_up, parcel_type='customer_to_courier')
                location.available_space-=1
                location.save()
                serializer = ParcelSerializer(storage)
                
                
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
        
        
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsDeliveryAdminUser])
def delivery_parcels(request):
    if request.method == "GET":
        cities = Parcel.objects.values_list('city', flat=True).distinct()
        # print(cities)
        data =[
            {'name': city,
             'parcels': Parcel.objects.filter(city=city).values()
             } for city in cities if city != None
            
            ]
        

        return Response(data, status=status.HTTP_200_OK)
    
    
@swagger_auto_schema(methods=['POST','DELETE'], request_body=UpdateLocationSerializer())
@api_view(['POST', 'DELETE'])
def update_location(request, location):
    
    centers = BoxLocation.objects.filter(location=location, is_active=True)
    if centers.count() == 0:
        raise ValidationError(detail="This location has no active centers")
    
    if request.method == 'POST':
        serializer = UpdateLocationSerializer(data=request.data)
        
        if serializer.is_valid():
            centers.update(location=serializer.validated_data['location'])
            data = {"message":"successful",
                    }
            
            return Response(data, status=status.HTTP_200_OK)
            
        else:
            errors = {"message":"failed",
                    "errors":serializer.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST) 
        
    
    elif request.method=='DELETE':
        centers.update(is_active=False)
        data = {
            "message":"success"
                        }
        return Response(data, status=status.HTTP_204_NO_CONTENT) 