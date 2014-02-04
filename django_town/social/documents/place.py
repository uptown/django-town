import mongoengine
from django_town.mongoengine_extension import OptionField, ResourceField
from django_town.social.define import PLACE_CATEGORIES, CONTACT_TYPES
from django_town.social.documents.thing import Thing, Photo
from django_town.social.resources.region import RegionResource


class Address(mongoengine.EmbeddedDocument):
    region = ResourceField(RegionResource())
    remains = mongoengine.ListField(mongoengine.StringField())
    remains_ascii = mongoengine.ListField(mongoengine.StringField())
    postal_code = mongoengine.StringField()

    meta = {
        'indexes': ['region']
    }


class Contact(mongoengine.EmbeddedDocument):
    type = OptionField(option=CONTACT_TYPES, default=0)
    value = mongoengine.StringField()


class Place(Thing):
    photo = mongoengine.ReferenceField(Photo)
    type = OptionField(option=PLACE_CATEGORIES, default=0)
    location = mongoengine.PointField()

    meta = {
        'indexes': ['type']
    }


class Organization(Place):
    address = mongoengine.EmbeddedDocumentField(Address)
    contacts = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Contact))


class LocalBusiness(Organization):
    opening_hours = mongoengine.StringField()
    closed = mongoengine.StringField()
    is_parking_available = mongoengine.BooleanField()


class FoodEstablishment(LocalBusiness):
    pass