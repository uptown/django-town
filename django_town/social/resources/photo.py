from django.core.files.images import get_image_dimensions

from django_town.rest.resources import MongoResource
from django_town.social.documents import Photo
from django_town.social.resources.user import UserResource
from django_town.helper.thumbnail import get_thumbnails


class PhotoResource(MongoResource):
    def pre_create(self, data, files, acceptable, required, exclude, request, request_kwargs, or_get):
        data['owner'] = UserResource()(request.oauth2_user.pk)
        dimensions = get_image_dimensions(files['source'])
        data['height'] = dimensions[1]
        data['width'] = dimensions[0]
        return data, files

    def serialize(self, resource_instance, options=None, request=None):
        ret = super(PhotoResource, self).serialize(resource_instance, options, request)
        source, width, height = Photo.source.storage.url(ret['source']), ret['width'], ret['height']
        ret['source'] = {'url': source, 'width': width, 'height': height}
        ret['sources'] = []
        ret['sources'] += get_thumbnails(source, (width, height), Photo.source.sizes)
        del ret['width'], ret['height']
        return ret

    class Meta:
        document = Photo
        cache_key_format = "_ut_photo:%(pk)s"
        create_acceptable = ['source']