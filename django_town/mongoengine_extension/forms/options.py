from django.utils import six
import warnings
from django.forms.forms import get_declared_fields
from django.forms.widgets import media_property
from django.core.exceptions import FieldError

from django_town.mongoengine_extension.forms.field_factory import fields_for_document
from django_town.mongoengine_extension.forms.base import BaseDocumentForm


ALL_FIELDS = '__all__'


class DocumentFormOptions(object):
    def __init__(self, options=None):
        self.document = getattr(options, 'document', None)
        self.fields = getattr(options, 'fields', None)
        self.exclude = getattr(options, 'exclude', None)
        self.widgets = getattr(options, 'widgets', None)
        self.localized_fields = getattr(options, 'localized_fields', None)
        self.labels = getattr(options, 'labels', None)
        self.help_texts = getattr(options, 'help_texts', None)
        self.error_messages = getattr(options, 'error_messages', None)


class DocumentFormMetaclass(type):
    def __new__(cls, name, bases, attrs):
        try:
            parents = [b for b in bases if issubclass(b, DocumentForm)]
        except NameError:
            # We are defining ModelForm itself.
            parents = None
        declared_fields = get_declared_fields(bases, attrs, False)
        new_class = super(DocumentFormMetaclass, cls).__new__(cls, name, bases,
                                                              attrs)
        if not parents:
            return new_class

        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        opts = new_class._meta = DocumentFormOptions(getattr(new_class, 'Meta', None))

        # We check if a string was passed to `fields` or `exclude`,
        # which is likely to be a mistake where the user typed ('foo') instead
        # of ('foo',)
        for opt in ['fields', 'exclude', 'localized_fields']:
            value = getattr(opts, opt)
            if isinstance(value, six.string_types) and value != ALL_FIELDS:
                msg = ("%(model)s.Meta.%(opt)s cannot be a string. "
                       "Did you mean to type: ('%(value)s',)?" % {
                           'model': new_class.__name__,
                           'opt': opt,
                           'value': value,
                       })
                raise TypeError(msg)

        if opts.document:
            # If a model is defined, extract form fields from it.

            if opts.fields is None and opts.exclude is None:
                # This should be some kind of assertion error once deprecation
                # cycle is complete.
                warnings.warn("Creating a ModelForm without either the 'fields' attribute "
                              "or the 'exclude' attribute is deprecated - form %s "
                              "needs updating" % name,
                              PendingDeprecationWarning, stacklevel=2)

            if opts.fields == ALL_FIELDS:
                # sentinel for fields_for_model to indicate "get the list of
                # fields from the model"
                opts.fields = None

            fields = fields_for_document(opts.document, opts.fields, opts.exclude,
                                         opts.widgets, opts.localized_fields, opts.labels,
                                         opts.help_texts, opts.error_messages)
            # make sure opts.fields doesn't specify an invalid field
            none_model_fields = [k for k, v in six.iteritems(fields) if not v]
            missing_fields = set(none_model_fields) - \
                             set(declared_fields.keys())
            if missing_fields:
                message = 'Unknown field(s) (%s) specified for %s'
                message = message % (', '.join(missing_fields),
                                     opts.document.__name__)
                raise FieldError(message)
            # Override default model fields with any custom declared ones
            # (plus, include all the other declared fields).
            fields.update(declared_fields)
        else:
            fields = declared_fields
        new_class.declared_fields = declared_fields
        new_class.base_fields = fields
        return new_class


class DocumentForm(six.with_metaclass(DocumentFormMetaclass, BaseDocumentForm)):
    pass