from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication
from delivery.models import DesignatedParcel
from account.permissions import IsDeliveryAdminUser
from delivery.serializers import DesignatedParcelSerializer
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
            serializer.save()
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



@api_view(['GET'])
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
    if obj.status != 'completed':
        obj.status = "completed"
        obj.save()
        #TODO: Send notification
    
        data = {
                    "message":"success",
                    }
                
        return Response(data, status=status.HTTP_200_OK)
    else:
        raise ValidationError(detail="This parcel has been delivered")
        
    