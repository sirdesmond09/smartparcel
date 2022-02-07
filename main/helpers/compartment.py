from main.models import BoxLocation, BoxSize, Parcel
from rest_framework.exceptions import ValidationError

def reduce_spaces(size:BoxSize, location:BoxLocation):
    if size.name == "small":
        location.available_small_space-=1
        location.save()
        return
    
    elif size.name == "medium":
        location.available_medium_space-=1
        location.save()
        return
    
    elif size.name == "large":
        location.available_large_space-=1
        location.save()
        return
    
    elif size.name == "xlarge":
        location.available_xlarge_space-=1
        location.save()
        return
    
    elif size.name == "xxlarge":
        location.available_xxlarge_space+=1
        location.save()
        return
    
    else:
        return 
    
    
def increase_spaces(size:BoxSize, location:BoxLocation):
    if size.name == "small":
        location.available_small_space+=1
        location.save()
        return
    
    elif size.name == "medium":
        location.available_medium_space+=1
        location.save()
        return
    
    elif size.name == "large":
        location.available_large_space+=1
        location.save()
        return
    
    elif size.name == "xlarge":
        location.available_xlarge_space+=1
        location.save()
        return
    
    elif size.name == "xxlarge":
        location.available_xxlarge_space+=1
        location.save()
        return
    
    else:
        return 

def get_compartment(location:BoxLocation, size:BoxSize):
    compartments_ = location.category.compartments.filter(size=size)
    # print(sizes)
    
    for compartment in compartments_:
        if Parcel.objects.filter(compartment=compartment, location=location, status="pending").exists():
            continue
        elif Parcel.objects.filter(compartment=compartment, location=location, status="assigned").exists():
            continue
        elif Parcel.objects.filter(compartment=compartment, location=location, status="dropped").exists():
            continue
        else:
            reduce_spaces(size,location)
            return compartment
    raise ValidationError(detail=f'Available {size.name} spaces used up for this location') 
    
       
        
def available_space(size:BoxSize, location:BoxLocation):
    if size.name == "small":
        return location.available_small_space
    elif size.name == "medium":
        return location.available_medium_space
    elif size.name == "large":
        return location.available_large_space
    elif size.name == "xlarge":
        return location.available_xlarge_space
    elif size.name == "xxlarge":
        return location.available_xxlarge_space
    else:
        return 0