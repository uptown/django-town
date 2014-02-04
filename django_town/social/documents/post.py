import mongoengine
import datetime
from django_town.social.documents.place import Place
from django_town.mongoengine_extension import OptionField, DynamicResourceField, ResourceIntField
from django_town.social.resources.user import UserResource
from django_town.social.resources.page import PageResource
from django_town.social.resources.oauth2 import ClientResource
from django_town.social.define import PRIVACY_OPTIONS


class Privacy(mongoengine.EmbeddedDocument):
    value = OptionField(option=PRIVACY_OPTIONS, default=0)
    allow = mongoengine.ListField(mongoengine.IntField(), default=[])
    deny = mongoengine.ListField(mongoengine.IntField(), default=[])


class Post(mongoengine.Document):
    client = ResourceIntField(ClientResource())

    # who
    from_ = DynamicResourceField((UserResource(), PageResource()), db_field="from")
    to_ = DynamicResourceField((UserResource(), PageResource()), db_field="to")
    tags = mongoengine.ListField(DynamicResourceField((UserResource(), PageResource())))

    # why, how
    content = mongoengine.StringField(max_length=2000, required=True)

    #what
    object = mongoengine.DynamicField()

    privacy = mongoengine.EmbeddedDocumentField(Privacy, default=lambda: Privacy(value=0))
    is_hidden = mongoengine.BooleanField(default=False)

    # where
    place = mongoengine.ReferenceField(Place)

    # when
    created = mongoengine.DateTimeField(default=datetime.datetime.now)
    modified = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {
        'indexes': ['from_', 'to_', 'tags', 'object']
    }

class Comment(mongoengine.Document):

    client = ResourceIntField(ClientResource())
    from_ = DynamicResourceField((UserResource(), PageResource()), db_field="from")

    post = mongoengine.ReferenceField(Post)
    content = mongoengine.StringField(max_length=2000)
    object = mongoengine.DynamicField()
    is_hidden = mongoengine.BooleanField(default=False)

    # when
    created = mongoengine.DateTimeField(default=datetime.datetime.now)
    modified = mongoengine.DateTimeField(default=datetime.datetime.now)


class PostLike(mongoengine.Document):
    from_ = DynamicResourceField((UserResource(), PageResource()), db_field="from")
    post = mongoengine.ReferenceField(Post)


class CommentLike(mongoengine.Document):
    from_ = DynamicResourceField((UserResource(), PageResource()), db_field="from")
    post = mongoengine.ReferenceField(Comment)


class Feed(mongoengine.Document):
    pass