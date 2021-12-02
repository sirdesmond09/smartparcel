from django.core.management.base import BaseCommand, CommandError
from main.models import BoxLocation

class Command(BaseCommand):
    help = 'Create Dummy Box locations'


    def handle(self, *args, **options):
        
        box_centers = [
            {
            'location':"Lekki",
            'center_name':"The Palms Shopping Mall",
            'address':'10, Fola Osibo Road, Lekki, Lagos, Nigeria',
            'no_of_compartment':5},
            {
            'location':"Lekki",
            'center_name':"Lennox Mall, Admiralty Way",
            'address':' 12, Layi Yusuf Crescent, Lekki, Lagos, Nigeria',
            'no_of_compartment':2},
            {
            'location':"Yaba",
            'center_name':"Spar, Tejuoso Market, Yaba",
            'address':'1-3, Ijaoye Street, Yaba, Nigeria',
            'no_of_compartment':2},
            {
            'location':"Lekki",
            'center_name':"The Palms Shopping Mall",
            'address':' 38, Olanrewaju Ninalowo Crescent, Lekki, Lagos, Nigeria',
            'no_of_compartment':5},
            {
            'location':"Yaba",
            'center_name':"Mini so, Tejuoso Market, Yaba",
            'address':'6 Araoti Street, Yaba, Lagos, Nigeria',
            'no_of_compartment':4},
            {
            'location':"Surulere",
            'center_name':"Leisure Mall",
            'address':'18,oyekan Street, Surulere, Lagos, Nigeria',
            'no_of_compartment':3},
            ]
        box = []
        for center in box_centers:
            box.append(BoxLocation(**center, available_space=center['no_of_compartment']))
            
        BoxLocation.objects.bulk_create(box)

        self.stdout.write(self.style.SUCCESS("Successfully added %s box locations" %len(box)))