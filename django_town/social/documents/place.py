import mongoengine

from django_town.mongoengine_extension import OptionField, ResourceField
from django_town.social.define import PLACE_CATEGORIES, CONTACT_TYPES
from django_town.social.documents.thing import Thing
from django_town.social.resources.region import RegionResource


class Address(mongoengine.EmbeddedDocument):
    region = ResourceField(RegionResource())
    postal_code = mongoengine.StringField()

    meta = {
        'indexes': [{'fields': ['region'], 'cls': False}],
    }


class Contact(mongoengine.EmbeddedDocument):
    type = OptionField(option=CONTACT_TYPES, default='phone')
    value = mongoengine.StringField()

    meta = {
        'indexes': [{'fields': [('type', 'value')], 'cls': False}],
    }


class Place(Thing):
    type = OptionField(option=PLACE_CATEGORIES, default='undefined')
    location = mongoengine.PointField(unique_with='name')
    verified = mongoengine.BooleanField(default=False)

    meta = {
        'indexes': [{'fields': ['type'], 'cls': False}],
    }

    def __unicode__(self):
        return str(self.name) + ' (' + str(mongoengine.PointField().to_dict(self.location)) + ')'



class Organization(Place):
    address = mongoengine.EmbeddedDocumentField(Address)
    contacts = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Contact))

    meta = {
        'indexes': [{'fields': ['contacts'], 'cls': False}],
    }


class LocalBusiness(Organization):
    opening_hours = mongoengine.StringField()
    closed = mongoengine.StringField()
    is_parking_available = mongoengine.BooleanField()

    meta = {
        'indexes': [{'fields': ['is_parking_available'], 'cls': False}],
    }


class FoodEstablishment(LocalBusiness):
    pass


class AdministrativeArea(mongoengine.Document):
    name = mongoengine.StringField()
    location = mongoengine.PointField(unique_with='name', unique=True)
    address = mongoengine.EmbeddedDocumentField(Address)
    level = mongoengine.IntField()
    northeast = mongoengine.PointField()
    southwest = mongoengine.PointField()

    meta = {
        'indexes': [{'fields': ['level'], 'cls': False}],
    }