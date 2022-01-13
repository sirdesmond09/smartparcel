from django.core.management.base import BaseCommand, CommandError
from main.models import BoxLocation
from main.models import create_box_key

class Command(BaseCommand):
    help = 'Create Dummy Box locations'


    def handle(self, *args, **options):
        
        boxes = BoxLocation.objects.filter(is_active=True)
        for center in boxes:
            center:BoxLocation
            center.center_apikey=create_box_key()
            center.save()
            

        self.stdout.write(self.style.SUCCESS("Successfully updated %s box locations" %len(boxes)))