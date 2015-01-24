from django.core.management.base import BaseCommand
from django_town.oauth2.models import Client, Service

class Command(BaseCommand):

    def handle(self, *args, **options):
        print(Client.objects.create(name=args[0], service=Service.objects.get(name=args[1])))