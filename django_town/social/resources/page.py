from django_town.rest.resources import ModelResource
from django_town.social.models import Page


class PageResource(ModelResource):
    model = Page
    cache_key_format = "_ut_page:%(pk)s"
    fields = ['id', 'name', 'about']