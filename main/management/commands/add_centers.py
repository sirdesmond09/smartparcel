from django.core.management.base import BaseCommand, CommandError
from main.models import BoxLocation

class Command(BaseCommand):
    help = 'Create Dummy Box locations'


    def handle(self, *args, **options):
        
        box_centers = [
            {
            'location':"Lekki",
            'address':"The Palms Shopping Mall"},
            {
            'location':"Lekki",
            'address':"Lennox Mall, Admiralty Way"},
            {
            'location':"Yaba",
            'address':"Spar, Tejuoso Market, Yaba"},
            {
            'location':"Lekki",
            'address':"The Palms Shopping Mall"},
            {
            'location':"Yaba",
            'address':"Mini so, Tejuoso Market, Yaba"},
            {
            'location':"Surulere",
            'address':"Leisure Mall"},
            ]
        box = []
        for center in box_centers:
            box.append(BoxLocation(**center))
            
        BoxLocation.objects.bulk_create(box)

        self.stdout.write(self.style.SUCCESS("Successfully added %s box locations" %len(box)))