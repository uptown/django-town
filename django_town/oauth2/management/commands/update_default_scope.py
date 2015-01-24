from django.core.management.base import BaseCommand
from django_town.oauth2.models import Client
from django_town.core.settings import OAUTH2_SETTINGS

class Command(BaseCommand):

    def handle(self, *args, **options):
        Client.objects.all().update(available_scope=OAUTH2_SETTINGS.default_scope)
        print Client.objects.all()[0].available_scope
        # print Client.objects.create(name=args[0], service=Service.objects.get(name=args[1]))