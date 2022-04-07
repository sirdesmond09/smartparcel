from django.core.management.base import BaseCommand, CommandError
from main.models import BoxLocation
import json


class Command(BaseCommand):
    help = 'Create Dummy Box locations'


    def handle(self, *args, **options):
        
        with open('C:/Users/BudgIT Guest/Desktop/projects/smart_parcel/prod_fire_cred.json', 'r') as f:
            info = json.load(f)
            credentials = json.dumps(info)
            
        with open('C:/Users/BudgIT Guest/Desktop/projects/smart_parcel/.env', 'a') as f:
            f.write(f'\nFIREBASE_CREDENTIALS={credentials}')
            
        
        self.stdout.write('firebase credentials updated')