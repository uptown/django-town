from django.core.management.base import BaseCommand
from django_town.oauth2.models import Service

class Command(BaseCommand):

    def handle(self, *args, **options):
        print(Service.objects.create(name=args[0]))