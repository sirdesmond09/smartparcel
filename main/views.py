from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import BoxLocation
from .serializers import BoxLocationSerializer, CustomerToCusomterSerializer, SelfStorageSerializer
import random
# Create your views here.

def generate_code(digit:int):
    pass

    
@api_view(['GET'])
def box_locations(request):
    if request.method == "GET":
        locations = BoxLocation.objects.values_list('location', flat=True).distinct()
        print(locations)
        data ={location: BoxLocation.objects.filter(location=location).values()  for location in locations}         

        return Response(data, status=status.HTTP_200_OK)
    

@swagger_auto_schema(methods=["POST"], request_body=SelfStorageSerializer())
@api_view(['POST'])
def self_storage(request):
    if request.method == 'POST':
        serializer = SelfStorageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {"message":"success",
                    "data":serializer.data}
            return Response(data, status=status.HTTP_200_OK)
        
        else:
            errors = {"message":"failed",
                    "errors":serializer.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        
@swagger_auto_schema(methods=["POST"], request_body=CustomerToCusomterSerializer())
@api_view(['POST'])
def customer_to_customer(request):
    if request.method == 'POST':
        serializer = CustomerToCusomterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {"message":"success",
                    "data":serializer.data}
            return Response(data, status=status.HTTP_200_OK)
        
        else:
            errors = {"message":"failed",
                    "errors":serializer.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)