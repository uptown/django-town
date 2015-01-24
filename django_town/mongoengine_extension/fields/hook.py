import operator
from django.utils.six import iteritems

from bson import SON, DBRef
from mongoengine.base import ALLOW_INHERITANCE, BaseDocument
from mongoengine.common import _import_class
from mongoengine import fields

from django_town.mongoengine_extension.fields.base import *


def to_dict_document(self, serializer=None):
    data = SON()
    data["_id"] = None
    # data['_cls'] = self._class_name

    for field_name in self:
        value = self._data.get(field_name, None)
        field = self._fields.get(field_name)
        if field is None and self._dynamic:
            field = self._dynamic_fields.get(field_name)
        if value and isinstance(field, (ResourceField, ResourceIntField, DynamicResourceField)):
            pass
            # value = value.to_dict(fields=field.fields)
        if value is not None:
            value = field.to_dict(value, serializer=serializer)

        # Handle self generating fields
        if value is None and field._auto_gen:
            value = field.generate()
            self._data[field_name] = value

        if value is not None:
            data[field.db_field] = value

    # If "_id" has not been set, then try and set it
    Document = _import_class("Document")
    if isinstance(self, Document):
        if data["_id"] is None:
            data["_id"] = self._data.get("id", None)

    if data['_id'] is None:
        data.pop('_id')

    # Only add _cls if allow_inheritance is True
    # if (not hasattr(self, '_meta') or
    # not self._meta.get('allow_inheritance', ALLOW_INHERITANCE)):
    #     data.pop('_cls')

    return data


def to_dict_for_default(self, value, serializer=None):
    return self.to_mongo(value)


def to_dict_for_complex(self, value, serializer=None):
    """Convert a Python type to a MongoDB-compatible type.
    """
    Document = _import_class("Document")
    EmbeddedDocument = _import_class("EmbeddedDocument")
    GenericReferenceField = _import_class("GenericReferenceField")

    if isinstance(value, basestring):
        return value

    if hasattr(value, 'to_dict'):
        if isinstance(value, Document):
            return GenericReferenceField().to_dict(value, serializer=serializer)
        cls = value.__class__
        val = value.to_dict(serializer=serializer)
        # If we its a document thats not inherited add _cls
        # if (isinstance(value, EmbeddedDocument)):
        # val['_cls'] = cls.__name__
        return val

    is_list = False
    if not hasattr(value, 'items'):
        try:
            is_list = True
            value = dict([(k, v) for k, v in enumerate(value)])
        except TypeError:  # Not iterable return the value
            return value

    if self.field:
        value_dict = dict([(key, self.field.to_dict(item, serializer=serializer))
                           for key, item in iteritems(value)])
    else:
        value_dict = {}
        for k, v in iteritems(value):
            if isinstance(v, Document):
                # We need the id from the saved object to create the DBRef
                if v.pk is None:
                    self.error('You can only reference documents once they'
                               ' have been saved to the database')

                # If its a document that is not inheritable it won't have
                # any _cls data so make it a generic reference allows
                # us to dereference
                meta = getattr(v, '_meta', {})
                allow_inheritance = (
                    meta.get('allow_inheritance', ALLOW_INHERITANCE)
                    is True)
                if not allow_inheritance and not self.field:
                    value_dict[k] = GenericReferenceField().to_dict(v, serializer=serializer)
                else:
                    collection = v._get_collection_name()
                    value_dict[k] = DBRef(collection, v.pk)
            elif hasattr(v, 'to_dict'):
                cls = v.__class__
                val = v.to_dict(serializer=serializer)
                # If we its a document thats not inherited add _cls
                # if (isinstance(v, (Document, EmbeddedDocument))):
                # val['_cls'] = cls.__name__
                value_dict[k] = val
            else:
                value_dict[k] = self.to_dict(v, serializer=serializer)

    if is_list:  # Convert back to a list
        return [v for k, v in sorted(value_dict.items(),
                                     key=operator.itemgetter(0))]
    return value_dict


def to_dict_for_point(self, value, serializer=None):
    if not isinstance(value, list):
        point = value['coordinates']
    else:
        point = value
    return {"latitude": point[1], "longitude": point[0]}


def to_dict_for_embedded_field(self, value, serializer=None):
    if not isinstance(value, self.document_type):
        return value
    return self.document_type.to_dict(value, serializer=serializer)


setattr(BaseDocument, 'to_dict', to_dict_document)

for field in fields.__all__:
    cls = getattr(fields, field)
    if field in ["ComplexBaseField", "ListField"]:
        setattr(cls, 'to_dict', to_dict_for_complex)
    elif field in ["PointField"]:
        setattr(cls, 'to_dict', to_dict_for_point)
    elif field in ["EmbeddedDocumentField"]:
        setattr(cls, 'to_dict', to_dict_for_embedded_field)
    elif not hasattr(cls, 'to_dict'):
        setattr(cls, 'to_dict', to_dict_for_default)
