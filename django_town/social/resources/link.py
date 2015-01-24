from django_town.rest.resources import MongoResource
from django_town.rest.exceptions import RestBadRequest
from django_town.social.documents import Link, EmbeddedPhoto
from django_town.utils.rand import generate_random_from_vschar_set
from django_town.utils.with3 import urlopen
from django.utils.six import StringIO
from django.core.files import File


class LinkResource(MongoResource):

    def pre_create(self, data, files, acceptable, required, exclude, request, request_kwargs, or_get):
        if 'photo' in files:
            photo = EmbeddedPhoto()
            photo.source.save(generate_random_from_vschar_set(50) + '.jpg', File(files['photo']), False)
            photo.height = photo.source.height
            photo.width = photo.source.width
            data['photo'] = photo
            del(files['photo'])
        elif 'photo_url' in data:
            file = StringIO(urlopen(data['photo_url']).read())
            if file:
                photo = EmbeddedPhoto()
                photo.source.save(generate_random_from_vschar_set(50) + '.jpg', File(file), False)
                photo.height = photo.source.height
                photo.width = photo.source.width
                data['photo'] = photo
                del(data['photo_url'])
            else:
                raise RestBadRequest()
        return data, files

    class Meta:
        document = Link
        cache_key_format = "_ut_link:%(pk)s"
        create_required = ['url']


link_public_resource = LinkResource()