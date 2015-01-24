from django_town.rest.resources import ModelResource
from django_town.social.models import Site


class SiteResource(ModelResource):

    class Meta:
        model = Site
        cache_key_format = "_ut_site:%(pk)s"
        # fields = ['id', 'name', 'about', 'category', 'liked', 'like_count', 'photo']

