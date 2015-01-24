import datetime
import mongoengine

from django_town.social.documents.place import Place
from django_town.social.documents.thing import Link

from django_town.mongoengine_extension import OptionField, DynamicResourceField, ResourceIntField, ThumbnailImageField,\
    ResourceReferenceField
from django_town.social.resources.user import UserResource
from django_town.social.resources.page import PageResource
from django_town.social.resources.feed import FeedResource
from django_town.social.resources.oauth2 import ClientResource
from django_town.social.define import PRIVACY_OPTIONS


class Privacy(mongoengine.EmbeddedDocument):
    value = OptionField(option=PRIVACY_OPTIONS, default='Global')
    allow = mongoengine.ListField(mongoengine.IntField(), default=[])
    deny = mongoengine.ListField(mongoengine.IntField(), default=[])


class Post(mongoengine.Document):
    # service = ResourceIntField(ServiceResource(), default=ServiceResource()(pk=1))
    client = ResourceIntField(ClientResource(filter=('name', 'service.id', 'service.name', 'id')),
                              default=ClientResource()(pk=1))

    # who
    _from = DynamicResourceField((UserResource(filter=('name', 'id', 'photo')),
                                  PageResource(filter=('name', 'id', 'photo'))), db_field="from")
    feed = ResourceIntField(FeedResource(filter=('name', 'id', 'photo')))
    tags = mongoengine.ListField(DynamicResourceField((UserResource(filter=('name', 'id', 'photo')),
                                                       PageResource(filter=('name', 'id', 'photo')))))

    title = mongoengine.StringField(max_length=100)
    content = mongoengine.StringField(max_length=4000)
    picture = ThumbnailImageField(sizes=[(200, None), (400, None)], upload_to="/image/post/photo")

    keywords = mongoengine.ListField(mongoengine.StringField())

    # what
    link = ResourceReferenceField(Link, exclude=['modified'], cache_key_format="_ut_link:%(pk)s")

    privacy = mongoengine.EmbeddedDocumentField(Privacy, default=lambda: Privacy(value=0))
    is_hidden = mongoengine.BooleanField(default=False)

    # where
    place = mongoengine.ReferenceField(Place)

    # when
    created = mongoengine.DateTimeField(default=datetime.datetime.now)
    modified = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'indexes': ['_from', 'feed', 'tags', '-created']
    }


class Comment(mongoengine.Document):
    client = ResourceIntField(ClientResource(filter=('name', 'service.id', 'service.name', 'id')),
                              default=ClientResource()(pk=1))
    _from = DynamicResourceField((UserResource(filter=('name', 'id', 'photo')),
                                  PageResource(filter=('name', 'id', 'photo'))), db_field="from")

    post = mongoengine.ReferenceField(Post)
    content = mongoengine.StringField(max_length=2000)
    object = mongoengine.DynamicField()
    is_hidden = mongoengine.BooleanField(default=False)

    # when
    created = mongoengine.DateTimeField(default=datetime.datetime.now)
    modified = mongoengine.DateTimeField(default=datetime.datetime.now)
    meta = {
        'indexes': ['_from', '-created']
    }


class PostLike(mongoengine.Document):
    _from = DynamicResourceField((UserResource(filter=('name', 'id', 'photo')),
                                  PageResource(filter=('name', 'id', 'photo'))), db_field="from", unique_with="post")
    created = mongoengine.DateTimeField(default=datetime.datetime.now)
    post = mongoengine.ReferenceField(Post)


class CommentLike(mongoengine.Document):
    _from = DynamicResourceField((UserResource(filter=('name', 'id', 'photo')),
                                  PageResource(filter=('name', 'id', 'photo'))), db_field="from", unique=True)
    created = mongoengine.DateTimeField(default=datetime.datetime.now)
    post = mongoengine.ReferenceField(Comment)


class Feed(mongoengine.Document):
    pass