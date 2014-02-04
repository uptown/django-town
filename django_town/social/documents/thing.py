import mongoengine
import datetime
from django_town.mongoengine_extension import DynamicResourceField, ResourceIntField
from django_town.social.resources.user import UserResource
from django_town.social.resources.page import PageResource
from django_town.social.resources.oauth2 import ServiceResource


class Thing(mongoengine.Document):
    service = ResourceIntField(ServiceResource(), default=ServiceResource()(pk=1))
    name = mongoengine.StringField()
    description = mongoengine.StringField(default="")
    created = mongoengine.DateTimeField(default=datetime.datetime.now)
    modified = mongoengine.DateTimeField(default=datetime.datetime.now)
    meta = {'allow_inheritance': True}


class Photo(mongoengine.Document):
    source = mongoengine.URLField(default=None)
    height = mongoengine.IntField(default=0)
    width = mongoengine.IntField(default=0)
    owner = DynamicResourceField((UserResource(), PageResource()))
    created = mongoengine.DateTimeField(default=datetime.datetime.now)


class Link(Thing):
    thumbnail = mongoengine.ReferenceField(Photo)
    url = mongoengine.URLField()


class Youtube(Thing):
    youtube_id = mongoengine.StringField()


class Album(Thing):
    photos = mongoengine.ListField(Photo)


class ThingLike(mongoengine.Document):
    from_ = DynamicResourceField((UserResource(), PageResource()), db_field="from")
    to_ = mongoengine.ReferenceField(Thing, db_field="to")