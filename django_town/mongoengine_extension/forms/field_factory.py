from django.utils.datastructures import SortedDict
from django.utils.text import capfirst
from django import forms

from django_town.mongoengine_extension.forms.fields import MongoCharField, MongoEmailField, MongoURLField, ListField, \
    ReferenceField, DocumentMultipleChoiceField, MapField


ALL_FIELDS = '__all__'

_form_field_map = {
    'stringfield': MongoCharField,
    'stringfield_choices': forms.TypedChoiceField,
    'stringfield_long': MongoCharField,
    'emailfield': MongoEmailField,
    'urlfield': MongoURLField,
    'intfield': forms.IntegerField,
    'intfield_choices': forms.TypedChoiceField,
    'floatfield': forms.FloatField,
    'decimalfield': forms.DecimalField,
    'booleanfield': forms.BooleanField,
    'booleanfield_choices': forms.TypedChoiceField,
    'datetimefield': forms.SplitDateTimeField,
    'referencefield': ReferenceField,
    'listfield': ListField,
    'listfield_choices': forms.MultipleChoiceField,
    'listfield_references': DocumentMultipleChoiceField,
    'mapfield': MapField,
    'filefield': forms.FileField,
    'imagefield': forms.ImageField,
}


def formfield_callback(self, form_class=None, choices_form_class=None, **kwargs):
    """
    Returns a django.forms.Field instance for this database Field.
    """
    defaults = {'required': self.required,
                'label': capfirst(self.verbose_name),
                'help_text': self.help_text}
    if self.default is not None:
        if callable(self.default):
            defaults['initial'] = self.default
            defaults['show_hidden_initial'] = True
        else:
            defaults['initial'] = self.default
    if self.choices:
        # Fields with choices get special treatment.
        include_blank = (self.blank or
                         not (self.has_default() or 'initial' in kwargs))
        defaults['choices'] = self.get_choices(include_blank=include_blank)
        defaults['coerce'] = self.to_python
        if self.null:
            defaults['empty_value'] = None
        if choices_form_class is not None:
            form_class = choices_form_class
        else:
            form_class = forms.TypedChoiceField
        # Many of the subclass-specific formfield arguments (min_value,
        # max_value) don't apply for choice fields, so be sure to only pass
        # the values that TypedChoiceField will understand.
        for k in list(kwargs):
            if k not in ('coerce', 'empty_value', 'choices', 'required',
                         'widget', 'label', 'initial', 'help_text',
                         'error_messages', 'show_hidden_initial'):
                del kwargs[k]
    defaults.update(kwargs)
    if form_class is None:
        form_class = _form_field_map.get(self.__class__.__name__.lower(), MongoCharField)

    if issubclass(form_class, ListField):
        return form_class(formfield_callback(self.field, **kwargs), **defaults)
    else:
        return form_class(**defaults)


def fields_for_document(document, fields=None, exclude=None, widgets=None, localized_fields=None,
                        labels=None, help_texts=None, error_messages=None):
    """
    Returns a ``SortedDict`` containing form fields for the given model.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned fields.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned fields, even if they are listed
    in the ``fields`` argument.

    ``widgets`` is a dictionary of model field names mapped to a widget.

    ``localized_fields`` is a list of names of fields which should be localized.

    ``labels`` is a dictionary of model field names mapped to a label.

    ``help_texts`` is a dictionary of model field names mapped to a help text.

    ``error_messages`` is a dictionary of model field names mapped to a
    dictionary of error messages.

    ``formfield_callback`` is a callable that takes a model field and returns
    a form field.
    """
    field_list = []
    ignored = []
    for each_field in document._fields.items():
        f = each_field[1]
        name = each_field[0]
        # if not getattr(f, 'editable', False):
        # continue
        if fields is not None and not name in fields:
            continue
        if exclude and name in exclude:
            continue

        kwargs = {}
        if widgets and name in widgets:
            kwargs['widget'] = widgets[name]
        if localized_fields == ALL_FIELDS or (localized_fields and name in localized_fields):
            kwargs['localize'] = True
        if labels and name in labels:
            kwargs['label'] = labels[name]
        if help_texts and name in help_texts:
            kwargs['help_text'] = help_texts[name]
        if error_messages and name in error_messages:
            kwargs['error_messages'] = error_messages[name]
        if hasattr(f, 'formfield'):
            formfield = f.formfield(**kwargs)
        else:
            formfield = formfield_callback(f, **kwargs)
        if formfield:
            field_list.append((name, formfield))
        else:
            ignored.append(name)
    field_dict = SortedDict(field_list)
    if fields:
        field_dict = SortedDict(
            [(f, field_dict.get(f)) for f in fields
             if ((not exclude) or (exclude and f not in exclude)) and (f not in ignored)]
        )
    return field_dict

