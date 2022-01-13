from main.models import BoxLocation, Parcel
import random


def get_compartment(location:BoxLocation):
    num_of_compartments = location.no_of_compartment
    
    while True:
        num = random.choice(range(1,num_of_compartments+1))
        if Parcel.objects.filter(compartment=num, location=location, status="pending").exists():
            continue
        elif Parcel.objects.filter(compartment=num, location=location, status="assigned").exists():
            continue
        elif Parcel.objects.filter(compartment=num, location=location, status="dropped").exists():
            continue
        else:
            break
        
    return num
        
