from django.db.models import EmailField, ImageField
from django_town.helper.thumbnail import ThumbnailFile

try:
    from django_extensions.db.fields.json import JSONField
    # raise ImportError
except ImportError:
    from django.utils import six
    # import six
    import json
    from decimal import Decimal
    from django.db import models
    from django.conf import settings
    from django.core.serializers.json import DjangoJSONEncoder

    class JSONField(six.with_metaclass(models.SubfieldBase, models.TextField)):

        def __init__(self, *args, **kwargs):
            default = kwargs.get('default', None)
            if default is None:
                kwargs['default'] = '{}'
            elif isinstance(default, (list, dict)):
                kwargs['default'] = DjangoJSONEncoder().encode(default)
            models.TextField.__init__(self, *args, **kwargs)

        def to_python(self, value):
            if value is None or value == '':
                return {}
            elif isinstance(value, six.string_types) or isinstance(value, six.text_type):
                return json.loads(value, parse_float=Decimal, encoding=settings.DEFAULT_CHARSET)
            else:
                return value

        def get_db_prep_save(self, value, connection):
            # print value
            if not isinstance(value, (list, dict)):
                return super(JSONField, self).get_db_prep_save("", connection=connection)
            else:
                return super(JSONField, self).get_db_prep_save(DjangoJSONEncoder().encode(value), connection=connection)

try:
    from south.modelsinspector import add_introspection_rules

    add_introspection_rules([], ["^django_town\.core\.fields\._EmailField"])
    add_introspection_rules([], ["^django_town\.core\.fields\.JSONField"])
    add_introspection_rules([], ["^django_town\.core\.fields\.ImageThumbsField"])
except ImportError:
    pass

from django_town.utils.rand import generate_random_from_vschar_set


class _EmailField(EmailField):
    def to_python(self, value):
        if value[0] == '#':
            return super(_EmailField, self).to_python(None)
        return super(_EmailField, self).to_python(value)

    def get_prep_value(self, value):
        return super(_EmailField, self).to_python(value)


class ImageThumbsField(ImageField):
    attr_class = ThumbnailFile
    """
    Usage example:
    ==============
    photo = ImageWithThumbsField(upload_to='images', sizes=((125,125),(300,200),)

    To retrieve image URL, exactly the same way as with ImageField:
        my_object.photo.url
    To retrieve thumbnails URL's just add the size to it:
        my_object.photo.url_125x125
        my_object.photo.url_300x200

    Note: The 'sizes' attribute is not required. If you don't provide it,
    ImageWithThumbsField will act as a normal ImageField

    How it works:
    =============
    For each size in the 'sizes' atribute of the field it generates a
    thumbnail with that size and stores it following this format:

    available_filename.[width]x[height].extension

    Where 'available_filename' is the available filename returned by the storage
    backend for saving the original file.

    Following the usage example above: For storing a file called "photo.jpg" it saves:
    photo.jpg          (original file)
    photo.125x125.jpg  (first thumbnail)
    photo.300x200.jpg  (second thumbnail)

    With the default storage backend if photo.jpg already exists it will use these filenames:
    photo_.jpg
    photo_.125x125.jpg
    photo_.300x200.jpg

    Note: django-thumbs assumes that if filename "any_filename.jpg" is available
    filenames with this format "any_filename.[widht]x[height].jpg" will be available, too.

    To do:
    ======
    Add method to regenerate thubmnails

    """
    def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, sizes=None, **kwargs):
        self.verbose_name=verbose_name
        self.name=name
        self.width_field=width_field
        self.height_field=height_field
        self.sizes = sizes
        super(ImageField, self).__init__(**kwargs)


class RandomNameUploadTo(object):
    def __init__(self, prefix, length=30):
        self.prefix = prefix
        self.length = length

    def __call__(self, instance, filename):
        return self.prefix + generate_random_from_vschar_set(self.length)