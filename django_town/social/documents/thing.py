import datetime

import mongoengine

from django_town.mongoengine_extension import DynamicResourceField, ResourceIntField, ThumbnailImageField
from django_town.social.resources.user import UserResource
from django_town.social.resources.page import PageResource
from django_town.social.resources.oauth2 import ServiceResource


class EmbeddedPhoto(mongoengine.EmbeddedDocument):
    source = ThumbnailImageField(sizes=[(200, None), (400, None)])
    height = mongoengine.IntField(default=0)
    width = mongoengine.IntField(default=0)


class Photo(mongoengine.Document):
    source = ThumbnailImageField(sizes=[(200, None), (400, None)], upload_to="/image/photo")
    height = mongoengine.IntField(default=0)
    width = mongoengine.IntField(default=0)
    owner = DynamicResourceField((UserResource(filter=('name', 'id', 'photo')),
                                  PageResource(filter=('name', 'id', 'photo'))))
    created = mongoengine.DateTimeField(default=datetime.datetime.now)


class Thing(mongoengine.Document):
    service = ResourceIntField(ServiceResource()) #, default=ServiceResource()(pk=1)
    name = mongoengine.StringField()
    description = mongoengine.StringField(default="")
    created = mongoengine.DateTimeField(default=datetime.datetime.now)
    modified = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'allow_inheritance': True,
        'indexes': [{'fields': ['service'], 'cls': False}, 'created']
    }

    def __unicode__(self):
        return self.name


class Link(Thing):
    photo = mongoengine.EmbeddedDocumentField(EmbeddedPhoto)
    url = mongoengine.URLField()
    author = mongoengine.StringField()
    tags = mongoengine.ListField(mongoengine.StringField())
    keywords = mongoengine.ListField(mongoengine.StringField())

    meta = {
        'indexes': ['keywords', 'tags',
            {'fields': ['url'], 'unique': True, 'sparse': True},]
    }


class Youtube(Thing):
    youtube_id = mongoengine.StringField()


class Album(Thing):
    photos = mongoengine.ListField(Photo)


class ThingLike(mongoengine.Document):
    _from = DynamicResourceField((UserResource(), PageResource()), db_field="from")
    _to = mongoengine.ReferenceField(Thing, db_field="to")


class ThingFollow(mongoengine.Document):
    _from = DynamicResourceField((UserResource(), PageResource()), db_field="from")
    _to = mongoengine.ReferenceField(Thing, db_field="to")