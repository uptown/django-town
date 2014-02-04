
from django.db.models import EmailField
try:
    # from django_extensions.db.fields.json import JSONField
    raise ImportError
except ImportError:
    import six
    from decimal import Decimal
    from django.db import models
    from django.conf import settings
    from django.core.serializers.json import DjangoJSONEncoder
    import json

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
            elif isinstance(value, str) or isinstance(value, unicode):
                return json.loads(value, parse_float=Decimal, encoding=settings.DEFAULT_CHARSET)
            else:
                return value

        def get_db_prep_save(self, value, connection):
            #print value
            if not isinstance(value, (list, dict)):
                return super(JSONField, self).get_db_prep_save("", connection=connection)
            else:
                return super(JSONField, self).get_db_prep_save(DjangoJSONEncoder().encode(value), connection=connection)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^django_town\.core\.fields\._EmailField"])
    add_introspection_rules([], ["^django_town\.core\.fields\.JSONField"])
except ImportError:
    pass


class _EmailField(EmailField):

    def to_python(self, value):
        if value[0] == '#':
            return super(_EmailField, self).to_python(None)
        return super(_EmailField, self).to_python(value)

    def get_prep_value(self, value):
        return super(_EmailField, self).to_python(value)