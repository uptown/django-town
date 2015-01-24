from django.forms.forms import BaseForm


class BaseDocumentForm(BaseForm):
    def __init__(self, data=None, files=None, instance=None, initial=None, **kwargs):
        if instance:
            if not initial:
                initial = {}
            initial.update(self.instance_to_initial(instance))
        self.instance = instance
        super(BaseDocumentForm, self).__init__(data=data, files=files, initial=initial, **kwargs)

    def instance_to_initial(self, instance):
        return {}
