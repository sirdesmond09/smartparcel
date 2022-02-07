from rest_framework.exceptions import NotAuthenticated, ValidationError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from account.permissions import IsAdminOrReadOnly, IsDeliveryAdminUser
from .models import BoxLocation, BoxSize, Category, Compartment, Parcel, Payments, BoxSize, get_partner
from .serializers import AddCategorySerializer, AddLocationSerializer, BoxLocationSerializer, AddCategorySerializer, BoxSizeSerializer, CategorySerializer, CompartmentSerialzer, CustomerToCourierSerializer, CustomerToCusomterSerializer, DropCodeSerializer, ParcelSerializer, PaymentsSerializer, PickCodeSerializer, SelfStorageSerializer, UpdateLocationSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .helpers.paystack import verify_payment
from .helpers.compartment import get_compartment, available_space
import random
import string
from django.utils import timezone
import csv
from django.http import HttpResponse
from .models import signer


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
        locations = BoxLocation.objects.filter(is_active=True).values_list('location', flat=True).distinct()
        data =[
            {'name': location,
             'centers': BoxLocation.objects.filter(location=location, is_active=True).values()
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
            allow_save = serializer.validated_data.pop('allow_save')
            payment_data = verify_payment(reference=reference, allow_save=allow_save, user=request.user) 
            
            if payment_data != False:
                size = serializer.validated_data.pop('size')
                try:
                    location = BoxLocation.objects.get(id=serializer.validated_data.pop('location'), is_active=True)
                except BoxLocation.DoesNotExist:
                    raise ValidationError(detail='Location unavailable')
                
                if available_space(size, location) == 0:
                    raise ValidationError(detail=f'Available {size.name} spaces used up for this location')
                
                
                pick_up, drop_off = generate_code(4)
                
                Payments.objects.create(**payment_data, user=request.user, payment_for='self_storage') 
                # print(serializer.validated_data)
                compartment = get_compartment(location, size)
                storage = Parcel.objects.create(**serializer.validated_data, user=request.user,location=location, drop_off=drop_off, pick_up=pick_up, parcel_type='self_storage', compartment=compartment)
                
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
            allow_save = serializer.validated_data.pop('allow_save')
            payment_data = verify_payment(reference=reference, allow_save=allow_save, user=request.user) 
            
            if payment_data != False:
                
                # print(serializer.validated_data)
                size = serializer.validated_data.pop('size')
                
                try:
                    location = BoxLocation.objects.get(id=serializer.validated_data.pop('location'), is_active=True)
                except BoxLocation.DoesNotExist:
                    raise ValidationError(detail='Location unavailable')
                
                if available_space(size, location) == 0:
                    raise ValidationError(detail=f'Available {size.name} spaces used up for this location')
                
                pick_up, drop_off = generate_code(4)
                
                Payments.objects.create(**payment_data, user=request.user, payment_for='customer_to_customer') 
                
                compartment = get_compartment(location, size)
                storage = Parcel.objects.create(**serializer.validated_data, user=request.user,location=location, drop_off=drop_off, pick_up=pick_up, parcel_type='customer_to_customer', compartment=compartment)
                
                
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
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def dashboard(request):
    c2c = Payments.objects.filter(payment_for='customer_to_customer').values_list('amount',flat=True)
    self_storage = Payments.objects.filter(payment_for='self_storage').values_list('amount',flat=True)
    courier = Payments.objects.filter(payment_for='customer_to_courier').values_list('amount',flat=True)
    
    
    dates = [(timezone.now() - timezone.timedelta(days=x)).date() for x in range(7) ]
    # print(dates)
    daily_stats = {
            str(date): {
                'customer_to_customer': {
                    "num_of_transactions":Payments.objects.filter(transaction_date__date=date,payment_for='customer_to_customer', is_active=True).count(),
                    
                    "sum_total" : sum(Payments.objects.filter(transaction_date__date=date, payment_for='customer_to_customer',is_active=True).values_list('amount', flat=True))
                    },
                'self_storage': {
                    "num_of_transactions":Payments.objects.filter(transaction_date__date=date,payment_for='self_storage', is_active=True).count(),
                    
                    "sum_total" : sum(Payments.objects.filter(transaction_date__date=date, payment_for='self_storage',is_active=True).values_list('amount', flat=True))
                    },
                'customer_to_courier': {
                    "num_of_transactions":Payments.objects.filter(transaction_date__date=date,payment_for='customer_to_courier', is_active=True).count(),
                    
                    "sum_total" : sum(Payments.objects.filter(transaction_date__date=date, payment_for='customer_to_courier',is_active=True).values_list('amount', flat=True))
                    },
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
        'customer_to_courier':{
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

        
@swagger_auto_schema(methods=["POST"], request_body=DropCodeSerializer())
@api_view(['POST'])
def drop_codes(request):
    
    serializer = DropCodeSerializer(data = request.data)
    if serializer.is_valid():
        key = signer.sign(serializer.validated_data.pop('apikey'))
        try:
            center = BoxLocation.objects.get(id = serializer.validated_data['id'], center_apikey=key, is_active=True)
        except BoxLocation.DoesNotExist:
            raise NotAuthenticated(detail={ "message": "failed",
                                           "errors": {
                                            "code": [
                                            "Authentication failed"
                                            ]
                                        }
                                        })
        
        parcel = serializer.change_status(center)
        
        if parcel != None:
            parcel:Parcel
            data = {
                    "message": "success",
                    "data": {
                        "id": parcel.id,
                        "compartment":parcel.compartment.number
                    }
                }
            return Response(data, status=status.HTTP_200_OK)
        
        else:
            data = {"message":"failed"
                    }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
    else:
            errors = {"message":"failed",
                    "errors":serializer.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(methods=["POST"], request_body=PickCodeSerializer())
@api_view(['POST'])
def pick_codes(request):
    
    serializer = PickCodeSerializer(data = request.data)
    if serializer.is_valid():
        key = signer.sign(serializer.validated_data.pop('apikey'))
        try:
            center = BoxLocation.objects.get(id = serializer.validated_data['id'], center_apikey=key, is_active=True)
            
        except BoxLocation.DoesNotExist:
            raise NotAuthenticated(detail={ "message": "failed",
                                           "errors": {
                                            "code": [
                                            "Authentication failed"
                                            ]
                                        }
                                    })
        
        parcel = serializer.change_status(center)
        if parcel != None:
            parcel:Parcel
            data = {
                    "message": "success",
                    "data": {
                        "id": parcel.id,
                        "compartment":parcel.compartment.number
                    }
                }
            return Response(data, status=status.HTTP_200_OK)
        
        else:
            data = {"message":"failed"
                    }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
    else:
            errors = {"message":"failed",
                    "errors":serializer.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)


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
            allow_save = serializer.validated_data.pop('allow_save')
            payment_data = verify_payment(reference=reference, allow_save=allow_save, user=request.user)  
            
            if payment_data != False:
                size = serializer.validated_data.pop('size')
                
                try:
                    location = BoxLocation.objects.get(id=serializer.validated_data.pop('location'), is_active=True)
                except BoxLocation.DoesNotExist:
                    raise ValidationError(detail='Location unavailable')
                
                if available_space(size, location) == 0:
                    raise ValidationError(detail=f'Available {size.name} spaces used up for this location') 
                
                
                pick_up, drop_off = generate_code(4)
                
                Payments.objects.create(**payment_data, user=request.user, payment_for='customer_to_courier') 
                # print(serializer.validated_data)
                compartment = get_compartment(location, size)
                storage = Parcel.objects.create(**serializer.validated_data, user=request.user,location=location, drop_off=drop_off, pick_up=pick_up, parcel_type='customer_to_courier', compartment=compartment,delivery_partner=get_partner())
                
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
             'parcels': Parcel.objects.filter(city=city, is_active=True).values()
             } for city in cities if city != None
            
            ]
        

        return Response(data, status=status.HTTP_200_OK)
    
    
@swagger_auto_schema(methods=['POST','DELETE'], request_body=UpdateLocationSerializer())
@api_view(['POST', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def update_location(request, location):
    
    centers = BoxLocation.objects.filter(location=location, is_active=True)
    if centers.count() == 0:
        raise ValidationError(detail="Does Not Exist")
    
    if request.method == 'POST':
        serializer = UpdateLocationSerializer(data=request.data)
        
        if serializer.is_valid():
            centers.update(location=serializer.validated_data['location'])
            data = {
                "message":"successful",
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
    
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_center_keys(request):
    centers = BoxLocation.objects.filter(is_active=True)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="center_api_keys.csv"'

    writer = csv.writer(response)
    
    writer.writerow([
            'ID',
            'center_name',
            'location',
            'center_address',
            'center_api_key',
            
        ])
    
    for center in centers:
        center:BoxLocation
        writer.writerow([
            center.id,
            center.center_name,
            center.location,
            center.address,
            signer.unsign(center.center_apikey)
        ])
        


    return response
    
    
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_keys(request):
    centers = BoxLocation.objects.filter(is_active=True)
    
    data = [{
        "ID":center.id,
        "center_name":center.center_name, 
        "location":center.location, 
        "address":center.address, 
        "api_key": signer.unsign(center.center_apikey) 
    } for center in centers]
    
    return Response(data, status=status.HTTP_200_OK)
    
    
    
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def all_parcels(request):
    
    parcels = Parcel.objects.filter(is_active=True)
    serializer = ParcelSerializer(parcels, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




@swagger_auto_schema(methods=["POST"], request_body=AddCategorySerializer())
@api_view(["GET",'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def add_category(request):
    
    if request.method=="GET":
        category = Category.objects.filter(is_active=True)
        
        serializer = CategorySerializer(category, many=True)
        data = {
                "message":"success",
                "data":serializer.data}
            
        return Response(data, status=status.HTTP_200_OK)
        
    elif request.method=='POST':
        serializer = AddCategorySerializer(data=request.data)
        
        if serializer.is_valid():
            category = serializer.create_category()
            
            category_serializer = CategorySerializer(category)
            data = {
                "message":"success",
                "data":category_serializer.data}
            
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            errors = {
                "message":"failed",
                "errors":serializer.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
       
@swagger_auto_schema(method='post', request_body=CompartmentSerialzer())
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def set_size(request, category_id,compartent_id):
    if request.method == 'POST':
        
        try:
            compartment = Compartment.objects.get(id=compartent_id, category=category_id)
            compartment
        except BoxLocation.DoesNotExist:
            data = {
                    'status'  : False,
                    'message' : "Does not exist"
                }

            return Response(data, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CompartmentSerialzer(compartment, data=request.data,partial=True)
        
        if serializer.is_valid():
            serializer.save()
            data = {
                "message":"success"
                }
            
            return Response(data, status=status.HTTP_202_ACCEPTED)
        else:
            errors = {
                "message":"failed",
                "errors":serializer.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(methods=["POST"], request_body=BoxSizeSerializer())
@api_view(["GET",'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminOrReadOnly])
def add_sizes(request):
    
    if request.method=="GET":
        sizes = BoxSize.objects.filter(is_active=True)
        
        serializer = BoxSizeSerializer(sizes, many=True)
        data = {
                "message":"success",
                "data":serializer.data}
            
        return Response(data, status=status.HTTP_200_OK)
        
    elif request.method=='POST':
        serializer = BoxSizeSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            data = {
                "message":"success",
                "data":serializer.data}
            
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            errors = {
                "message":"failed",
                "errors":serializer.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        
@swagger_auto_schema(methods=['PUT', 'DELETE'], request_body=BoxSizeSerializer())
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def size_detail(request, size_id):
    
    
    try:
        obj = BoxLocation.objects.get(id = size_id, is_active=True)
    
    except BoxLocation.DoesNotExist:
        data = {
                'status'  : False,
                'message' : "Does not exist"
            }

        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BoxSizeSerializer(obj)
        
        data = {
                'status'  : True,
                'message' : "Successful",
                'data' : serializer.data,
            }

        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = BoxSizeSerializer(obj, data = request.data, partial=True) 

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
