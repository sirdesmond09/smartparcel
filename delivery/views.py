from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication
from delivery.models import DesignatedParcel
from account.permissions import IsDeliveryAdminUser
from delivery.serializers import DesignatedParcelSerializer, VerifyDeliveryCodeSerializer
from main.views import generate_code
from main.helpers.vonagesms import send_sms
# Create your views here.

@swagger_auto_schema(method='post', request_body=DesignatedParcelSerializer())
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsDeliveryAdminUser])
def assign_parcel(request):
    if request.method == 'GET':
        obj = DesignatedParcel.objects.filter(is_active=True)
        serializer =DesignatedParcelSerializer(obj, many=True)
        data = {
                "message":"success",
                "data":serializer.data
                }
            
        return Response(data, status=status.HTTP_200_OK)
        
    
    elif request.method == 'POST':
        serializer = DesignatedParcelSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['delivery_user']
            parcel = serializer.validated_data['parcel']
            if user.role != 'delivery_user':
                raise PermissionDenied(detail="This user cannot be assigned a parcel")
            if DesignatedParcel.objects.filter(parcel = parcel).exists() or parcel.status == 'assigned':
                raise ValidationError(detail="Parcel already assigned to another delivery person")
            
            _, delivery_code = generate_code(6)
            print(delivery_code)
            designated = DesignatedParcel.objects.create(**serializer.validated_data, delivery_code=delivery_code)
            parcel.status = 'assigned'
            parcel.save()
            serializer = DesignatedParcelSerializer(designated)
            
            try:
                send_sms(reason='delivery_code', code =delivery_code, phone =parcel.phone, address=None)
            finally:
                data = {
                    "message":"success",
                    "data":serializer.data
                    }
                
                return Response(data, status=status.HTTP_201_CREATED)
        else:
            errors = {
                "message":"failed",
                "errors":serializer.errors
                }
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(methods=['PUT', 'DELETE'], request_body=DesignatedParcelSerializer())
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsDeliveryAdminUser])
def assign_parcel_detail(request, id):
    try:
        obj = DesignatedParcel.objects.get(id=id, is_active=True)
    except DesignatedParcel.DoesNotExist:
        errors = {
                "message":"failed",
                "errors":'Designated parcel not found'
                }
        return Response(errors, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer =DesignatedParcelSerializer(obj)
        data = {
                "message":"success",
                "data":serializer.data
                }
            
        return Response(data, status=status.HTTP_200_OK)
        
    
    elif request.method == 'PUT':
        serializer = DesignatedParcelSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = {
                "message":"success",
                "data":serializer.data
                }
            
            return Response(data, status=status.HTTP_202_ACCEPTED)
        else:
            errors = {
                "message":"failed",
                "errors":serializer.errors
                }
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'DELETE':
        obj.delete()
        data = {
                "message":"success"
                }
            
        return Response(data, status=status.HTTP_204_NO_CONTENT)
    
    
    

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_designated_parcels(request):
    user = request.user
    
    obj = user.designated.filter(is_active=True, status='pending')
    serializer = DesignatedParcelSerializer(obj, many=True)
    
    data = {
                "message":"success",
                "data":serializer.data
                }
            
    return Response(data, status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['POST'], request_body=VerifyDeliveryCodeSerializer())
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def mark_complete(request, designated_parcel_id):
    try:
        obj = DesignatedParcel.objects.get(id=designated_parcel_id, is_active=True)
    except DesignatedParcel.DoesNotExist:
        errors = {
                "message":"failed",
                "errors":'Designated parcel not found'
                }
        return Response(errors, status=status.HTTP_404_NOT_FOUND)
    
    if obj.delivery_user != request.user:
        raise PermissionDenied(detail="You do not have permission to alter this parcel.")
    
    serializer = VerifyDeliveryCodeSerializer(data=request.data)
    if serializer.is_valid():
        
        complete = serializer.verify_code(obj)
        if complete==True:        
            data = {
                    "message":"success",
                }
                    
            return Response(data, status=status.HTTP_200_OK)
            
        
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_delivered_parcels(request):
    user = request.user
    
    obj = user.designated.filter(is_active=True, status='completed')
    serializer = DesignatedParcelSerializer(obj, many=True)
    
    data = {
                "message":"success",
                "data":serializer.data
                }
            
    return Response(data, status=status.HTTP_200_OK)